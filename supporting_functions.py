import os
import openpyxl as xl


def make_ana_def(conf_filename, signals_filename):
    """
    Call this function right in the place where new DEF should be.
    """
    if not os.path.isfile(conf_filename):
        print(f"The File {conf_filename} is not found!")
        return
    if '.xlsx' not in conf_filename:
        print('File needs to be in .xlsx format!')
        return
    if not os.path.isfile(signals_filename):
        print(f"The File {signals_filename} is not found!")
        return
    if '.xlsx' not in signals_filename:
        print('File needs to be in .xlsx format!')
        return
    print('Processing generated analogs list for _DEF_ making...')
    conf_wb = xl.load_workbook(conf_filename, read_only=True)
    wb = xl.load_workbook(signals_filename, read_only=False)
    if 'ana_def_config' in conf_wb.sheetnames:
        config_sheet = conf_wb['ana_def_config']
        signals_sheet = wb['generated_list']
        print('Reading configuration...')
    else:
        print('No configuration found!')
        return
    analogs_signal_type_def_dictionary = {}
    # Filling up dictionaries out of ana_config workbook
    for row in range(1, config_sheet.max_row + 1):
        signal_type_cell = config_sheet.cell(row, 1)        # e.g. Температура
        signal_type_def_cell = config_sheet.cell(row, 2)    # e.g. T_
        analogs_signal_type_def_dictionary[signal_type_cell.value] = signal_type_def_cell.value
    # Comparing parsed signal names to dictionary keys
    for idx in range(2, signals_sheet.max_row + 1):
        signals_sheet_cell = signals_sheet.cell(idx, 4)
        plcnum_sheet_cell = signals_sheet.cell(idx, 3)
        signal_name_frase = str(signals_sheet_cell.value)
        signal_name_words = signal_name_frase.split(" ")
        if plcnum_sheet_cell.value is not None:
            if 'A1' in plcnum_sheet_cell.value:
                analog_signal_plcnum = 'ANA1_'
            elif 'A2' in plcnum_sheet_cell.value:
                analog_signal_plcnum = 'ANA2_'
            elif 'A3' in plcnum_sheet_cell.value:
                analog_signal_plcnum = 'ANA3_'
            elif 'A4' in plcnum_sheet_cell.value:
                analog_signal_plcnum = 'ANA4_'
            else:
                analog_signal_plcnum = 'NEED TO ADD MORE PLCS IN CODE!!!!!'
        else:
            analog_signal_plcnum = '-------'
        result = 'DEF_' + analog_signal_plcnum
        for pos in signal_name_words:
            if pos in analogs_signal_type_def_dictionary:
                # print(pos)
                if analogs_signal_type_def_dictionary.get(pos) is not None and pos != 'Резерв':
                    result += str(analogs_signal_type_def_dictionary.get(pos)) + '_'
                else:
                    result = ''
        if result != '':
            print(result[:-1:].upper())


# testing call
make_ana_def('config_file.xlsx', 'AI.xlsx')