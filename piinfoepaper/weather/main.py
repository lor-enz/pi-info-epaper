


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    import logging
    import sys
    import piinfoepaper.mytime as mytime
    flip = False
    if len(sys.argv) > 1:
        if sys.argv[1].lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup']:
            flip = True
    print(f'Flip: {flip}')
    logging.basicConfig(level=logging.INFO)
    logging.info(f'## Start at {mytime.current_time_hr()}')

    from databook import Databook
    from paper import Paper

    book = Databook()
    paper = Paper(book, flip)

    paper.draw_data()