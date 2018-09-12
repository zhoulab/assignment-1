import os
import csv
from collections import OrderedDict

BASE_DIR = os.path.dirname(os.getcwd())


class AnnoFile(object):
    """Class for storing annotation file information

    Attributes
    ----------
    filepath
        absolute path of .anno file
    filename
        filename of .anno path
    name
        filename without extension ".anno"
    folder
        directory that `filename` is in
    header
        list of column names
    rows
        list of row dicts
    """

    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.name = self.filename[:-5]
        self.folder = os.path.basename(os.path.dirname(filepath))
        self.parse()

    def parse(self):
        """Parse self.filepath to get header and rows"""
        with open(self.filepath) as f:
            reader = csv.reader(f, delimiter='\t')
            self.header = ['PeakID' if 'PeakID' in col_name else col_name
                           for col_name in reader.next()]
            self.rows = [dict(zip(self.header, row))
                         for row in reader]
            for row in self.rows:
                for col in row:
                    if col in ['Start', 'End'] and row[col].isdigit():
                        row[col] = int(row[col])

    def get_occurences(self, col, values, exact=True, ignore_vals=False):
        """Return generator of row dicts containing matching `values` under `col`

        Parameters
        ----------
        col : str
        values : str or list
        fpath : str
        exact : bool
            define whether occurences should partially contain
            or match `values` exactly.
        ignore_vals : bool
            search for rows NOT containing matching `values` under `col`
        """
        if type(values) is str:
            values = [values]
        for row in self.rows:
            if not ignore_vals:
                if ((exact and row[col] in values) or
                   (not exact and any([val in row[col]
                                       for val in values]))):
                    yield row
            else:
                if ((exact and row[col] not in values) or
                   (not exact and all([val not in row[col]
                                       for val in values]))):
                    yield row

    def save_rows(self, rows, output_dir, desired_cols=None, save_name=None):
        """Save a bed-format file in `output_dir` containing `rows`.

        Parameters
        ----------
        rows : iterable of rows
        output_dir : filepath
        desired_cols : list of str
            columns to save with (default all columns)
        save_name : str
            filename to save as (default self.filename)
        """
        if not desired_cols:
            desired_cols = self.header
        if not save_name:
            save_name = self.filename
        with open(os.path.join(output_dir, save_name), 'w') as f:
            fwriter = csv.writer(f, delimiter='\t')
            fwriter.writerow(desired_cols)
            for row in rows:
                fwriter.writerow([row[col] for col in desired_cols])


def create_dir(dirpath):
    """Return `dirpath` and create if it doesn't exist
    **Parent directory of `dirpath` must already exist.
    """
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    return dirpath


def prompt_for_folder(dirpath):
    """Prompt user for a folder from dirpath."""
    all_folders = next(os.walk(dirpath))[1]
    folder = ''
    while folder not in all_folders:
        folder = raw_input('Enter folder to use [{}]: '
                           .format('/'.join(all_folders)))
    return folder


def prompt_for_folders(dirpath):
    """Prompt user for list of folders from `dirpath`

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
    import matplotlib
    matplotlib.use('Agg')
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
        legend = ax.legend(wedges, labels, loc='center left',
                           bbox_to_anchor=(1, .5), prop=font_props)
        plt.savefig(os.path.join(plots_dir, file + '.png'),
                    bbox_extra_artists=(legend,), bbox_inches='tight')
        plt.gcf().clear()


def do_anno_count():
    """Generate count files and pie plots with pre-defined parameters.

    Write occurence count data into tab-delimited txt file.
    Data is fetched from get_occurences and stored in `file_data`.

    Variables
    ---------
    folders : list of str
        sample folders to use (under data/Annos)
    search_values : list of str
    val_colors : list of str
        hex colors for corresponding element in ordered `values`
    output_dir : filepath (str)
        directory to save all results
    plots_dir : filepath (str)
        directory to save plot JPEGs
        create subdirectories for each anno folder
    file_data : dict
        see `generate_occurence_counts()`
    """
    annos_dir_path = os.path.join(BASE_DIR, 'data/Annos')
    folders = prompt_for_folders(annos_dir_path)
    if not folders:
        return -1
    search_values = ['Intergenic', 'intron', 'exon', 'promoter-TSS',
                     'TTS', "5' UTR", "3' UTR", 'non-coding']
    val_colors = ['#4D4D4D', '#5DA5DA', '#FAA43A', '#60BD68',
                  '#F17CB0', '#B2912F', '#B276B2', '#DECF3F']
    output_dir = create_dir(os.path.join(BASE_DIR, 'results',
                                         'P53-ChIPSeq-Anno_count'))
    plots_dir = create_dir(os.path.join(output_dir, 'plots'))
    for anno_folder in folders:
        anno_subdir_path = os.path.join(annos_dir_path, anno_folder)
        plots_subdir = create_dir(os.path.join(plots_dir,
                                               anno_folder + '-count_plots'))
        print ('{}: finding occurences of values under the '
               '"Annotation" column... ').format(anno_folder)
        anno_fpaths = [os.path.join(anno_subdir_path, f)
                       for f in next(os.walk(anno_subdir_path))[2]
                       if '.anno' in f]
        annos = [AnnoFile(fpath) for fpath in anno_fpaths]
        fnames = [anno_obj.name for anno_obj in annos]
        folder = annos[0].folder
        with open(os.path.join(output_dir, folder + '-count.txt'), 'w') as f:
            filewriter = csv.writer(f, delimiter='\t')
            filewriter.writerow(['Values'] + fnames)
            print 'Getting counts...',
            file_data = {fname: OrderedDict() for fname in fnames}
            for anno_obj in annos:
                for val in search_values:
                    file_data[anno_obj.name][val] = len(list(anno_obj.get_occurences(
                                                             'Annotation', val,
                                                             exact=False)))
            for value in search_values:
                filewriter.writerow([value] + [file_data[fname][value]
                                               for fname in fnames])
            filewriter.writerow(['Total'] + [sum(file_data[fname].values())
                                             for fname in fnames])
        print 'done. Saved at: "{}"'.format(anno_folder + '-count.txt')
        print 'Creating pie plots...',
        generate_pie_plots(file_data, search_values, val_colors, plots_subdir)
        print 'done. Saved at: "{}"'.format(plots_subdir)


def do_gene_search():
    """
    Data is fetched from get_occurences and stored in a variable
    then printed in a formatted output.

    Variables
    ---------
    gene_name: str
        Gene name to search for under the column 'Gene Name'
    files: list of str

    Data Structures
    ---------------
    data: [(filename1, [row1, row2, ...]),
           (filename2, [row1, row2, ...]), ...]
    """
    output_dir = create_dir(os.path.join(BASE_DIR, 'results',
                                         'P53-ChIPSeq-Anno_gene-search'))
    annos_dir_path = os.path.join(BASE_DIR, 'data/Annos')
    folder = prompt_for_folder(annos_dir_path)
    anno_subdir_path = os.path.join(BASE_DIR, 'data/Annos', folder)
    anno_fpaths = [os.path.join(anno_subdir_path, f)
                   for f in next(os.walk(anno_subdir_path))[2]
                   if '.anno' in f]

    print ('Find occurences of a gene under the "Gene Name"'
           'column for "{}"'.format(folder))
    gene_input = raw_input('Enter gene name: ')
    annos = [AnnoFile(fpath) for fpath in anno_fpaths]
    samples = [anno_obj.name for anno_obj in annos]
    matched_rows = {anno_obj.name:
                    list(anno_obj.get_occurences('Gene Name', gene_input))
                    for anno_obj in annos}

    out_fname = '{}_{}.txt'.format(folder, gene_input)
    with open(os.path.join(output_dir, out_fname), 'w') as f:
        fwriter = csv.writer(f, delimiter='\t')
        fwriter.writerow(['Filename', 'Count',
                          'Occurences (start, end, length)'])
        for sample in samples:
            print ('{}: {} row(s) found with Gene Name={}'
                   .format(sample, len(matched_rows[sample]), gene_input))
            occurences = ['({},{},{})'.format(row['Start'], row['End'],
                                              row['End'] - row['Start'] + 1)
                          for (i, row) in enumerate(matched_rows[sample])]
            fwriter.writerow([sample, len(matched_rows[sample]),
                              ','.join(occurences)])


def do_remove_repeats():
    """Save .bed files with lines that have
    Homer Genomic Annotation categories other than repeats.
    Also save full-row copies of non-repeat lines and repeat lines only

    Variables
    ---------
    folders : list of str
        sample folders to use (under data/Annos)
    categories : set of str
        non-repeat Homer Genomic Annotation categories
    search_col : str
        column that contains that contains 'repeats' information
    output_cols : list
        columns to use for line output
    """
    annos_dir_path = os.path.join(BASE_DIR, 'data/Annos')
    folders = prompt_for_folders(annos_dir_path)
    if not folders:
        return -1
    categories = {'TSS', 'TTS', 'exon', "5' UTR", "3' UTR",
                  'CpG', 'intron', 'Intergenic', 'non-coding'}
    search_col = 'Detailed Annotation'
    output_cols = ['Chr', 'Start', 'End', 'PeakID']
    output_dir = create_dir(os.path.join(BASE_DIR, 'results',
                                         'P53-ChIPSeq-Anno_remove-repeats'))
    for anno_subdir_name in folders:
        anno_subdir_path = os.path.join(annos_dir_path, anno_subdir_name)
        output_subdir = create_dir(os.path.join(output_dir,
                                                anno_subdir_name +
                                                '-no_repeats'))
        full_rows_subdir = create_dir(os.path.join(output_subdir,
                                                   'no_repeats_full_rows'))
        repeats_subdir = create_dir(os.path.join(output_subdir,
                                                 'repeats_only_full_rows'))
        files = [fname for fname in next(os.walk(anno_subdir_path))[2]
                 if '.anno' in fname]
        fpaths = [os.path.join(anno_subdir_path, fname)
                  for fname in files]
        for fpath in fpaths:
            anno_obj = AnnoFile(fpath)
            print 'Processing {}...'.format(anno_obj.name)
            out_file = anno_obj.name + '-no_repeats.bed'
            full_rows_file = anno_obj.name + '-no_repeats.anno'
            repeats_file = anno_obj.name + '-repeats_only.anno'
            rows = list(anno_obj.get_occurences(search_col, categories,
                                                exact=False))
            anno_obj.save_rows(rows, output_subdir,
                               desired_cols=output_cols, save_name=out_file)
            anno_obj.save_rows(rows, full_rows_subdir,
                               save_name=full_rows_file)
            repeat_rows = anno_obj.get_occurences(search_col, categories,
                                                  exact=False, ignore_vals=True)
            anno_obj.save_rows(repeat_rows, repeats_subdir,
                               save_name=repeats_file)
