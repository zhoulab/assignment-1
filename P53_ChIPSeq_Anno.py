import os
import csv
from collections import OrderedDict

BASE_DIR = os.path.dirname(os.getcwd())


def create_dir(dirpath):
    """Return `dirpath` and create if it doesn't exist
    **The directory `os.path.dirname(dirpath)` must already exist.
    """
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    return dirpath


def parse_anno_file(fpath):
    """Return each row in a dictionary format.
    Use name 'PeakID' for column name rather than 'PeakID (...)'

    Returns
    -------
    ({header1: value1-1, header2: value1-2, ...},
     {header1: value2-1, header2: value2-2, ...}, ...)
        Where header(j) is the jth header in the file and
        value(i)-(j) is the value under the jth header and ith row in file.
    """
    with open(fpath) as f:
        reader = csv.reader(f, delimiter='\t')
        header = ['PeakID' if 'PeakID' in col_name else col_name
                  for col_name in reader.next()]
        for row in reader:
            yield dict(zip(header, (value for value in row)))


def generate_occurence_count_files(fpaths, col, values, output_dir,
                                   plots_dir, val_colors):
    """Write occurence count data into tab-delimited txt file.
    Data is fetched from get_occurences and stored in `file_data`.

    Parameters
    ----------
    fpaths : list of str
        Filepaths of .anno files to search.
        All must be under the same folder (see variable `folder`)
    col : str
        Column of .anno file to search under
    values : list of str
        Values to search for under `col`

    Variables
    ---------
    folder : str
        name of common directory amongst files in `fpaths`
    files : list of str
        filenames without trailing ".anno"
    file_data : {fname1: OD{v1: count_v1, v2: count_v2, ...},
                 fname2: OD{v1: count_v1, v2: count_v2, ...}, ...}
    """
    folder = os.path.basename(os.path.dirname(fpaths[0]))
    files = [os.path.basename(path)[:-5] for path in fpaths]
    with open(os.path.join(output_dir, folder + '-results.txt'), 'w') as file:
        filewriter = csv.writer(file, delimiter='\t')
        filewriter.writerow(['Values'] + files)
        print 'Getting counts...'
        file_data = {fname: OrderedDict() for fname in files}
        for fpath, fname in zip(fpaths, files):
            anno_file_rows = list(parse_anno_file(fpath))
            for value in values:
                file_data[fname][value] = len(list(get_occurences(anno_file_rows,
                                              col, value, fpath, exact=False)))
        for value in values:
            filewriter.writerow([value] + [file_data[fname][value]
                                           for fname in files])
        filewriter.writerow(['Total'] + [sum(file_data[fname].values())
                                         for fname in files])
    print 'Creating pie plots...'
    generate_pie_plots(file_data, values, val_colors, plots_dir)


def generate_pie_plots(file_data, values, colors, plots_dir):
    """Create pie plots for each file in `file_data.keys()`

    Parameters
    ----------
    file_data : dict
        see `generate_occurence_counts()`
    values : list of str
    colors : list of str
        hex colors for corresponding element in ordered `values`
    plots_dir : filepath (str)
        directory to save plot JPEGs
    """
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import FontProperties

    font_props = FontProperties()
    font_props.set_size('small')

    for file in file_data.keys():
        if sorted(file_data[file].keys()) != sorted(values):
            print 'Search values do not match for {}.'.format(file)
            continue
        if sum(file_data[file].values()) is 0:
            print 'No counts for {}.'.format(file)
            continue
        ax = plt.subplot(111)
        ax.axis('equal')

        counts = [file_data[file][value] for value in values]
        plt.title(file)
        wedges, texts = plt.pie(counts, colors=colors, startangle=90)
        for w in wedges:
            w.set_linewidth(0)

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        labels = ['{} ({:.1f}%)'.format(value, 100 * file_data[file][value] /
                                        float(sum(file_data[file].values())))
                  for value in values]
        ax.legend(wedges, labels, loc='center left',
                  bbox_to_anchor=(1, .5), prop=font_props)
        plt.savefig(os.path.join(plots_dir, file + '.jpg'))
        plt.gcf().clear()


def get_occurences(anno_file_rows, col, values, fpath, exact=True):
    """Return rows containing matching `values` under `col`
    Parameters
    ----------
    anno_file_rows : iterable of dict
        see `parse_anno_file`
    col : str
    values : str or list
    fpath : str
    exact : bool
        define whether occurences should partially contain
        or match `values` exactly.

    Returns
    -------
    generator of dicts
    """
    if type(values) is str:
        values = [values]
    for row in anno_file_rows:
        if exact:
            if row[col] in values:
                yield row
        else:
            if any([val in row[col] for val in values]):
                yield row


def get_no_repeat_lines(anno_file_rows, fpath, desired_cols,
                        search_col='Detailed Annotation',
                        categories=None):
    """
    Return `desired_cols` from lines that are not
    in the repetitive sequence regions (repeats)

    Parameters
    ----------
    anno_file_rows : iterable of dict
        see `parse_anno_file`
    fpath : str
        filepath of .anno file
    categories : set of str
        non-repeat Homer Genomic Annotation categories
    desired_cols : list
        columns to return
    search_col : column that contains that contains 'repeats' information
    """
    if not categories:
        categories = {'TSS', 'TTS', 'exon', "5' UTR", "3' UTR",
                     'CpG', 'intron', 'Intergenic', 'non-coding'}
    rows = get_occurences(anno_file_rows, search_col, categories, fpath)
    for row in rows:
        yield [row[col] for col in desired_cols]


def prompt_for_folders(dirpath):
    """Prompt user for list of folders from `dirpath`.

    Return list of folder names if all are valid subdirectories of `dirpath`,
    otherwise `False` and display invalid inputs.
    """
    all_folders = next(os.walk(dirpath))[1]
    print 'Input subdirectories of {}'.format(dirpath)
    folders = raw_input('Enter folder(s) to use, separated by ",": ')
    folders = [f.strip() for f in folders.split(',')] if folders else []
    if not folders:
        print 'No folders specified.'
    elif not all([f in all_folders for f in folders]):
        invalid_folders_str = ', '.join([f for f in folders
                                         if f not in all_folders])
        print 'Some invalid directories ({})'.format(invalid_folders_str)
        return False
    return folders


def do_anno_count():
    """Generate count files and pie plots with pre-defined parameters.
    Variables
    ---------
    folders : list of str
        sample folders to use (under data/Annos)
    """
    annos_dir_path = os.path.join(BASE_DIR, 'data/Annos')
    folders = prompt_for_folders(annos_dir_path)
    if not folders:
        return -1
    search_values = ['non-coding', 'Intergenic', 'intron', 'exon',
                     'promoter-TSS', 'TTS', "5' UTR", "3' UTR"]
    val_colors = ['#4D4D4D', '#5DA5DA', '#FAA43A', '#60BD68',
                  '#F17CB0', '#B2912F', '#B276B2', '#DECF3F']
    output_dir = create_dir(os.path.join(BASE_DIR, 'results',
                                         'P53-ChIPSeq-Anno-results'))
    plots_dir = create_dir(os.path.join(output_dir, 'plots'))

    for anno_subdir_name in folders:
        anno_subdir_path = os.path.join(annos_dir_path, anno_subdir_name)
        plots_subdir = create_dir(os.path.join(plots_dir,
                                               anno_subdir_name + '_plots'))
        print ('{}: finding occurences of values under the '
               '"Annotation" column... ').format(anno_subdir_name)
        anno_fpaths = [os.path.join(anno_subdir_path, f)
                       for f in next(os.walk(anno_subdir_path))[2]
                       if '.anno' in f]
        generate_occurence_count_files(anno_fpaths, 'Annotation',
                                       search_values, output_dir,
                                       plots_subdir, val_colors)
        print 'Done. Saved at: "{}"'.format(anno_subdir_name + '-results.txt')


def do_remove_repeats():
    """Save .bed files with lines that have
    Homer Genomic Annotation categories other than repeats.

    Variables
    ---------
    folders : list of str
        sample folders to use (under data/Annos)
    output_cols : list
        columns to use for line output
    """
    annos_dir_path = os.path.join(BASE_DIR, 'data/Annos')
    folders = prompt_for_folders(annos_dir_path)
    if not folders:
        return -1
    output_cols = ['Chr', 'Start', 'End', 'PeakID']
    output_dir = create_dir(os.path.join(BASE_DIR, 'results',
                                         'P53-ChIPSeq-Anno_remove-repeats'))
    for anno_subdir_name in folders:
        anno_subdir_path = os.path.join(annos_dir_path, anno_subdir_name)
        output_subdir = create_dir(os.path.join(output_dir,
                                                anno_subdir_name +
                                                '-no_repeats'))
        files = next(os.walk(anno_subdir_path))[2]
        files = [f[:-5] for f in files]  # remove .anno from filenames
        for fname in files:
            fpath = os.path.join(anno_subdir_path, fname + '.anno')
            print 'Processing {}...'.format(fname)
            anno_file_rows = list(parse_anno_file(fpath))
            out_file = os.path.join(output_subdir, fname + '-no_repeats.bed')
            with open(out_file, 'w') as f:
                fwriter = csv.writer(f, delimiter='\t')
                fwriter.writerow(output_cols)
                for line in get_no_repeat_lines(anno_file_rows,
                                                fpath, output_cols):
                    fwriter.writerow(line)
