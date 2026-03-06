import os.path as osp
import glob


def pytest_addoption(parser):
    parser.addoption(
        "--dtaDir",
        action="store",
        default=osp.join(osp.dirname(osp.abspath(__file__)), 'dta'),
        help="The directory with dta files."
    )
    parser.addoption(
        "--refDir",
        action="store",
        default=osp.join(osp.dirname(osp.abspath(__file__)), 'reference'),
        help="The directory with reference solutions."
    )


def pytest_generate_tests(metafunc):
    dta_dir = metafunc.config.getoption('--dtaDir')
    ref_dir = metafunc.config.getoption('--refDir')

    # Generate list of standalone files to compare
    dta_files = [
        f for f in glob.glob(dta_dir + '/**/*.DTA', recursive=True)
        if '__' not in osp.basename(f)
    ]
    ref_files = [
        osp.join(ref_dir, f"{osp.splitext(osp.basename(f))[0]}.npz")
        for f in dta_files
    ]

    # Add continuation file groups as a single entry per base name
    cont_bases = sorted(set(
        osp.basename(f).split('__')[0]
        for f in glob.glob(osp.join(dta_dir, '*__*.DTA'))
    ))
    for base in cont_bases:
        dta_files.append(
            sorted(glob.glob(osp.join(dta_dir, f"{base}__*.DTA"))))
        ref_files.append(osp.join(ref_dir, f"{base}-cont.npz"))

    metafunc.parametrize("dta_file, ref_file", list(zip(dta_files, ref_files)))
