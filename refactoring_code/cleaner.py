import shutil
from pathlib import Path
import re

#////////////////start_clean_function////////////////

def clean(folder:Path):
    #normalize
    CYRILLIC_SYMBOLS = 'абвгдеєжзіийклмнопрстуфхцчшщьюяєїґ'
    TRANSLATION = ("a", "b", "v", "h", "d", "e", "ie", "j", "z", "i", "y", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
                "f", "kh", "ts", "ch", "sh", "shch", "", "iy", "ia", "e", "yi", "h")
    ACCORD = dict()
    for cyril, latin in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        ACCORD[ord(cyril)] = latin
        ACCORD[ord(cyril.upper())] = latin.capitalize()

    def normalize(name: str) -> str:
        translate_name = re.sub(r'[^\w.]', '_', name.translate(ACCORD))
        return translate_name
    #parser
    JPEG_IMG = []
    JPG_IMG = []
    PNG_IMG = []
    SVG_IMG = []
    #'MP3', 'OGG', 'WAV', 'AMR'
    MP3_AUDIO = []
    OGG_AUDIO = []
    WAV_AUDIO = []
    AMR_AUDIO = []
    #'AVI', 'MP4', 'MOV', 'MKV'
    MP4_VIDEO = []
    AVI_VIDEO = []
    MOV_VIDEO = []
    MKV_VIDEO = []
    #'DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX, PY
    DOC_DOC = []
    DOCX_DOC = []
    TXT_DOC = []
    PDF_DOC = []
    XLSX_DOC = []
    PPTX_DOC = []
    PY_DOC = []
    #'ZIP', 'GZ', 'TAR'
    ZIP_ARCH = []
    GZ_ARCH = []
    TAR_ARCH = []
    NOT_DEFINED = []

    REGISTER_EXTENSION = {
        'JPEG': JPEG_IMG,
        'JPG': JPG_IMG,
        'PNG': PNG_IMG,
        'SVG': SVG_IMG,
        'OGG': OGG_AUDIO,
        'WAV': WAV_AUDIO,
        'AMR': AMR_AUDIO,            
        'MP3': MP3_AUDIO,
        'MP4': MP4_VIDEO,
        'AVI': AVI_VIDEO,
        'MOV': MOV_VIDEO,
        'MKV': MKV_VIDEO,
        'DOC': DOC_DOC,
        'DOCX': DOCX_DOC,
        'TXT': TXT_DOC,
        'PDF': PDF_DOC,
        'XLSX': XLSX_DOC,
        'PPTX': PPTX_DOC,
        'PY': PY_DOC,
        'ZIP': ZIP_ARCH,
        'GZ': GZ_ARCH,
        'TAR': TAR_ARCH
    }

    FOLDERS = []
    EXTENSIONS = set()
    UNKNOWN = set()

    def get_extension(name: str) -> str:
        return Path(name).suffix[1:].upper()  
    #folder
    def scan(folder: Path):
        for item in folder.iterdir():
            if item.is_dir(): 
                if item.name not in ('archives', 'video', 'audio', 'documents', 'images', 'not_defined'):
                    FOLDERS.append(item)
                    scan(item)
                continue
            extension = get_extension(item.name)  # gex file extention
            full_name = folder / item.name  # full path to file
            if not extension:
                NOT_DEFINED.append(full_name)
            else:
                try:
                    REGISTER_EXTENSION[extension].append(full_name)
                    EXTENSIONS.add(extension)
                except KeyError:
                    UNKNOWN.add(extension) 
                    NOT_DEFINED.append(full_name)

    def handle_media(file_name: Path, target_folder: Path):
        target_folder.mkdir(exist_ok=True, parents=True)
        file_name.replace(target_folder / normalize(file_name.name))

    def handle_archive(file_name: Path, target_folder: Path):
        target_folder.mkdir(exist_ok=True, parents=True)
        folder_for_file = target_folder / normalize(file_name.name.replace(file_name.suffix, ''))
        folder_for_file.mkdir(exist_ok=True, parents=True)
        try:
            shutil.unpack_archive(str(file_name.absolute()), str(folder_for_file.absolute()))
        except shutil.ReadError:
            folder_for_file.rmdir()
            return file_name.unlink()

    def main_cleaner(folder: Path):
        scan(folder)
        for file in JPEG_IMG:
            handle_media(file, folder / 'images' / 'JPEG')
        for file in JPG_IMG:
            handle_media(file, folder / 'images' / 'JPG')
        for file in PNG_IMG:
            handle_media(file, folder / 'images' / 'PNG')
        for file in SVG_IMG:
            handle_media(file, folder / 'images' / 'SVG')

        for file in MP3_AUDIO:
            handle_media(file, folder / 'audio' / 'MP3')
        for file in OGG_AUDIO:
            handle_media(file, folder / 'audio' / 'OGG')
        for file in WAV_AUDIO:
            handle_media(file, folder / 'audio' / 'WAV')  
        for file in AMR_AUDIO:
            handle_media(file, folder / 'audio' / 'AMR')  

        for file in AVI_VIDEO:
            handle_media(file, folder / 'video' / 'AVI')
        for file in MP4_VIDEO:
            handle_media(file, folder / 'video' / 'MP4')
        for file in MOV_VIDEO:
            handle_media(file, folder / 'video' / 'MOV')                                    
        for file in MKV_VIDEO:
            handle_media(file, folder / 'video' / 'MKV')

        for file in DOC_DOC:
            handle_media(file, folder / 'documents' / 'DOC')
        for file in DOCX_DOC:
            handle_media(file, folder / 'documents' / 'DOCX')        
        for file in TXT_DOC:
            handle_media(file, folder / 'documents' / 'TXT')        
        for file in PDF_DOC:
            handle_media(file, folder / 'documents' / 'PDF')        
        for file in XLSX_DOC:
            handle_media(file, folder / 'documents' / 'XLSX') 
        for file in PPTX_DOC:
            handle_media(file, folder / 'documents' / 'PPTX')               
        for file in PY_DOC:
            handle_media(file, folder / 'documents' / 'PY')        

        for file in NOT_DEFINED:
            handle_media(file, folder / 'not_defined')

        for file in ZIP_ARCH:
            handle_archive(file, folder / 'archives' / 'ZIP')
        for file in GZ_ARCH:
            handle_archive(file, folder / 'archives' / 'GZ') 
        for file in TAR_ARCH:
            handle_archive(file, folder / 'archives' / 'TAR')               

        for folder in FOLDERS[::-1]: #delete empty folders
            try:
                folder.rmdir()
            except OSError:
                print(f'Error during remove folder {folder}')
        return REGISTER_EXTENSION, UNKNOWN
       
    if folder:
        folder_path = Path(folder)
        exstention, unknown = main_cleaner(folder_path)
        return  {key: value for key, value in exstention.items() if value}, unknown 
#/////////////End_clean_function/////////////