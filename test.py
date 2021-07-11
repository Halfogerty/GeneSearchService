import pytest

from main import run_query


class TestRunQuery:
    def test_empty_query(self):
        assert run_query("", "homo_sapiens", 10) == ({"message": "Query string must not be empty"}, 404)

    def test_empty_species(self):
        assert run_query("brc", "", 10) == ({"message": "Species must not be empty"}, 404)

    def test_species_does_not_exist(self):
        assert run_query("brc", "human person", 10) == \
               ({"message": "Species 'human person' does not exist in the gene_autocomplete table"},  404)

    def test_non_integer_limit_raises_typerror(self):
        with pytest.raises(TypeError):
            run_query("brc", "homo_sapiens", "10")

    def test_run_query_successful(self):
        assert run_query("brc", "homo_sapiens", 10) == ({"data": ["BRCA1", "BRCA2", "BRCC3", "BRCC3P1"]}, 200)
