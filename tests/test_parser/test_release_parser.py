from datetime import date

from figure_parser.gsc import GSCShipment


def test_gsc_shipment():
    gs = GSCShipment()

    assert gs.keys()
    assert gs.values()

    for k in gs.keys():
        assert isinstance(k, date)

    for products in gs.values():
        for p in products:
            assert 'jan' in p
            assert 'url' in p
