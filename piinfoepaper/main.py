import logging
import mytime as mytime
from storage import retrieve, store
from os.path import exists


def run_covid_screen(config: dict):
    import covid.databook as covidbook
    from paper_controller import PaperController
    logging.info(f'## Start covid display at {mytime.current_time_hr()}')
    book = covidbook.Databook()
    layout = book.get_paper_layout(config)
    paper_controller = PaperController(layout)


def run_weather_screen(config: dict):
    import weather.databook as weatherbook
    from paper_controller import PaperController
    logging.info(f'## Start weather display at {mytime.current_time_hr()}')
    book = weatherbook.Databook()
    layout = book.get_paper_layout(config)
    paper_controller = PaperController(layout)


def decide_what_to_run(config: dict):
    dt = mytime.ts2dt(mytime.current_time())
    # if 15 < dt.minute < 45:
    #     logging.info("Skipping because: 15 < dt.minute < 45")
    #     return
    if 14 <= dt.hour < 18:
        run_covid_screen(config)
    else:
        run_weather_screen(config)


default_config = {
    'flip': False
}


def load_config():
    file_path = '/home/pi/paper-config.json'
    if not exists(file_path):
        file_path = '/home/pi/pi-info-epaper/paper-config.json'
        if not exists(file_path):
            return default_config
    json_data = retrieve(file_path)
    config = {}
    config['flip'] = json_data['flip']
    logging.info(f"loaded Config: {config}")
    return config


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    config = load_config()
    decide_what_to_run(config)
    # run_weather_screen(config)
    # run_covid_screen(config)
