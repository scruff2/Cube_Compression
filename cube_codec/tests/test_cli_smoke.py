from cube_codec.cli import build_parser


def test_cli_parser_smoke() -> None:
    parser = build_parser()
    args = parser.parse_args(["inspect-cube", "--cube-dir", "artifacts"])
    assert args.cmd == "inspect-cube"
