
import argparse

from proyectoiabd.pipelines.appointments_pipeline import run_appointments_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Eco-Scheduling Optimizer CLI"
    )

    parser.add_argument(
        "--mode",
        type=str,
        default="pipeline",
        choices=["pipeline"],
        help="Modo de ejecución"
    )

    args = parser.parse_args()

    if args.mode == "pipeline":
        run_appointments_pipeline()


if __name__ == "__main__":
    main()