import argparse

from generator.generator import run_simulation


def main():
    parser = argparse.ArgumentParser(prog="ecom_data_generator")

    parser.add_argument("-u", "--user_count", type=int)
    parser.add_argument("--truncate_table", action='store_true',
                        help="truncate existing tables")
    args = parser.parse_args()

    user_count = args.user_count
    truncate_table = args.truncate_table
    run_simulation(user_count=user_count, truncate_table=truncate_table)


if __name__ == "__main__":
    main()
