from line_factory.specs import expected_images, valid_count


def test_static_sticker_counts_and_names():
    assert valid_count("static_sticker", 8)
    assert not valid_count("static_sticker", 9)
    names = [e.filename for e in expected_images("static_sticker", 8)]
    assert names == ["main.png", "tab.png", "01.png", "02.png", "03.png", "04.png", "05.png", "06.png", "07.png", "08.png"]


def test_regular_emoji_counts_and_names():
    assert valid_count("regular_emoji", 8)
    assert valid_count("regular_emoji", 40)
    assert not valid_count("regular_emoji", 41)
    names = [e.filename for e in expected_images("regular_emoji", 8)]
    assert names == ["tab.png", "001.png", "002.png", "003.png", "004.png", "005.png", "006.png", "007.png", "008.png"]
