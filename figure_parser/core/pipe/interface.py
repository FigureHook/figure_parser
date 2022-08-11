from typing import Protocol, TypeVar

Product_T = TypeVar('Product_T')


class PipeInterface(Protocol[Product_T]):
    @staticmethod
    def process(product_item: Product_T) -> Product_T:
        raise NotImplementedError
