import logging
import mytime as mytime


def run_covid_screen():
    import covid.databook as covidbook
    from paper_controller import PaperController
    logging.info(f'## Start covid display at {mytime.current_time_hr()}')
    book = covidbook.Databook()
    layout = book.get_paper_layout()
    paper_controller = PaperController(layout)


def run_weather_screen():
    import weather.databook as weatherbook
    from paper_controller import PaperController
    logging.info(f'## Start weather display at {mytime.current_time_hr()}')
    book = weatherbook.Databook()
    layout = book.get_paper_layout()
    paper_controller = PaperController(layout)


def decide_what_to_run():
    dt = mytime.ts2dt(mytime.current_time())

    if 10 < dt.minute < 50:
        return
    if 13 < dt.hour < 19:
        run_covid_screen()
    else:
        run_weather_screen()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    decide_what_to_run()

