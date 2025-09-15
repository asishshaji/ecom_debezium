import argparse

from generator.generator import run_simulation


def main():
    parser = argparse.ArgumentParser(prog="ecom_data_generator")

    parser.add_argument("-u", "--user_count", type=int)
    args = parser.parse_args()

    user_count = args.user_count
    run_simulation(user_count=user_count)

if __name__ == "__main__":
    main()
