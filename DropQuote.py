import random
from utils import split_word_via_api, is_letter_char, safe_upper


class DropQuote:
    def __init__(self, quote: str, language: str = 'English', parsed_chars: list = None):
        self.language = language
        self.quote = safe_upper(quote)

        # Split into logical characters via API
        if parsed_chars:
            self.chars = parsed_chars
        else:
            self.chars = split_word_via_api(self.quote, self.language)

        # Standard width for Drop Quote
        self.width = 15

        self.columns = [self.letters_in_column(i) for i in range(self.width)]

    def split_quote(self):
        rows = []
        row = []

        for i, letter in enumerate(self.chars, start=1):

            # Determine cell type
            if is_letter_char(letter):
                cell = {'char': letter, 'type': 'blank'}
            elif letter == ' ':
                cell = {'char': ' ', 'type': 'space'}
            else:
                cell = {'char': letter, 'type': 'punct'}

            row.append(cell)

            # End of row
            if i % self.width == 0:
                rows.append(row)
                row = []

        if row:
            # Pad the last row with empty spaces to keep the grid even
            while len(row) < self.width:
                row.append({'char': ' ', 'type': 'space'})
            rows.append(row)

        return rows

    def letters_in_column(self, col):
        letters = [
            ch
            for ch in self.chars[col::self.width]
            if is_letter_char(ch)
        ]

        random.shuffle(letters)
        return letters


if __name__ == '__main__':
    q = 'Everybody has a plan till they get punched in the face'
    q1 = "We're going up, up, up, it's our moment. You know together we're glowing. Gonna be, gonna be Golden."

    d = DropQuote(q1)

    for row in d.split_quote():
        print(*row)

    for column in d.columns:
        print(column)
