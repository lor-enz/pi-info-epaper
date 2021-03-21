# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def maybe_9_min_update():
    # Use a breakpoint in the code line below to debug your script.
    # Press Ctrl+F8 to toggle the breakpoint.
    import databook as db
    import paper as pap
    book = db.Databook()
    paper = pap.Paper(book)
    paper.maybe_refresh_all_covid_data()
    paper.partial_refresh_vac_for(9 * 60 + 30)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    import logging
    import mytime as mytime

    logging.basicConfig(level=logging.DEBUG)
    logging.info(f'## Start at {mytime.current_time_hr()}')
    maybe_9_min_update()
