import pdfkit


def pdfconvert(file):
    converted = pdfkit.from_file(file, 'out.pdf')
    return converted