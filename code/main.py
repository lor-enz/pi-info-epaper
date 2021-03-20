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
    paper.partial_refresh_vacc_for_minutes(9)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    maybe_9_min_update()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
