from my_rabbit import set_config, RabbitConfig, get_config


def test_set_config_from_config():
    conf_1 = RabbitConfig()
    set_config(config=conf_1)

    conf_2 = get_config()
    assert conf_1 == conf_2


def test_set_config_from_params():
    set_config()

    conf_1 = RabbitConfig()
    conf_2 = get_config()
    assert conf_1 == conf_2
