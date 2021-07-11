from flask import Flask
from flask_restful import Resource, Api, reqparse
from mysql.connector import connect, Error


app = Flask(__name__)
api = Api(app)


def run_query(query_string, species, limit):
    try:
        if query_string == "":
            return {"message": "Query string must not be empty"}, 404
        if species == "":
            return {"message": "Species must not be empty"}, 404

        with connect(host="ensembldb.ensembl.org", port="3306", database="ensembl_website_102",
                     user='anonymous') as connection:
            with connection.cursor() as cursor:

                # Inform the user if the species does not exist in the table
                species_check_query = """SELECT 1 
                                         FROM gene_autocomplete 
                                         WHERE species = %s 
                                         LIMIT 1"""
                cursor.execute(species_check_query, (species,))
                species_check_result = cursor.fetchall()
                if len(species_check_result) == 0:
                    return {
                               "message": "Species '{}' does not exist in the gene_autocomplete table".format(species)
                           }, 404

                # Enforce that the limit is an integer for security
                if not isinstance(limit, int):
                    raise TypeError("The limit must be an integer")

                # Set upper bound on query limit to prevent expensive queries
                limit = min(limit, 1000)

                # Append wildcard operator to query string to perform prefix search
                query_string += "%"

                gene_search_query = """SELECT * FROM gene_autocomplete
                                       WHERE display_label LIKE %s AND species=%s
                                       LIMIT {}""".format(limit)
                val_tuple = (query_string, species)

                cursor.execute(gene_search_query, val_tuple)
                result = cursor.fetchall()
                return {
                           "data": sorted([row[2] for row in result])
                       }, 200
    except Error as e:
        print(e)


class GeneSuggest(Resource):
    def get(self):
        parser = reqparse.RequestParser()

        parser.add_argument('query', required=True, type=str)
        parser.add_argument('species', required=True, type=str)
        parser.add_argument('limit', required=True, type=int)
        args = parser.parse_args()
        return run_query(args['query'], args['species'], args['limit'])


api.add_resource(GeneSuggest, '/gene_suggest')

if __name__ == "__main__":
    app.run()
