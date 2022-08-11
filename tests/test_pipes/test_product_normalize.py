import pytest
from figure_parser.core.entity.product import ProductBase
from figure_parser.core.pipe.nomalization_pipe import (
    ProductGeneralFieldstNormalizer, ProductWorkerFieldstNormalizer,
    _normalize, general_normalize, worker_normalize)


class TestProductTextUtils:
    def test_general_attribute_normalization(self):
        text_should_be_half_width = "ＫＡＤＯＫＡＷＡ"
        text_with_duplicate_space = "too  much spaces Ver."
        text_with_weird_quotation = "hello ’there’"

        assert general_normalize(
            text_should_be_half_width) == "KADOKAWA"
        assert general_normalize(
            text_with_duplicate_space) == "too much spaces Ver."
        assert general_normalize(
            text_with_weird_quotation) == "hello 'there'"

    def test_worker_attribute_normalization(self):
        text_with_full_width_brackets = " (Hello, there)"
        text_with_no_space_before_bracket = "Master(HW)"
        text_with_no_space_before_square_bracket = "Newbie[NW]"

        assert worker_normalize(
            text_with_full_width_brackets) == "(Hello, there)"
        assert worker_normalize(
            text_with_no_space_before_bracket) == "Master (HW)"
        assert worker_normalize(
            text_with_no_space_before_square_bracket) == "Newbie (NW)"

    def test_list_attribute_normalization(self, product: ProductBase):
        ProductGeneralFieldstNormalizer.process(product)
        ProductWorkerFieldstNormalizer.process(product)

    def test_falsy_value_normalization(self):
        value = ''
        assert _normalize(value, lambda x: x) == value

        value = []  # type: ignore
        assert _normalize(value, lambda x: x) == value

        value = None
        assert _normalize(value, lambda x: x) == value  # type: ignore

    def test_raise_type_error(self):
        with pytest.raises(TypeError):
            _normalize(123, lambda x: x)  # type: ignore
