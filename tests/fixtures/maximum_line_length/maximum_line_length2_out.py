class Command(LoadDataCommand):

    option_list = LoadDataCommand.option_list + (make_option("-d",
        "--no-signals", dest="use_signals", default=True,
        help='Disconnects all signals during import', action="store_false"),)
