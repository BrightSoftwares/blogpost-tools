---
author: full
categories:
- data-analysis
description: You are working inside a Google Spreadsheet where a formula needs to
  copied down to the last row of the sheet. You also need the formula to be added
  automatically when a new row is added to the Google Sheet.
image: https://sergioafanou.github.io/blog/assets/images/12.jpg
lang: en
layout: flexstart-blog-single
ref: howtocopy_a_formula_downanentirecolumn
silot_terms: google data analysis
tags:
- spreadsheet
- productivity
- dataanalysis
title: How to Copy a Formula Down an Entire Column in Google Sheets
toc: true
---

You are working inside a [[2023-11-03-google-sheets-shortcuts|Google]] Spreadsheet where a formula needs to copied down to the last row of the sheet. You also need the formula to be added automatically when a new row is added to the [[2023-05-02-how-to-add-cells-in-google-sheets|Google]] Sheet.
There are several ways to solve this problem.

# Copy Formula Down in Google Sheets

The easiest approach to copy down formulas is to use the fill handle in Google Sheets. Write your formula in the first row of your spreadsheet, and then point your mouse to the lower right corner of the formula cell.

The pointer changes into a fill handle (black plus symbol) that you can drag to the last row of the sheet. The fill handle will not just copy down the formulas to all the adjacent cells but also copies the visual formatting.
If you need to copy the formulas across cells but sans any formatting, select the cell that contains the formatting and press Ctrl+C to copy it to the clipboard. Next, select the range where that formula needs to applied, right-click, choose Paste Special and Paste Formula only.

# Apply Formula to the Entire Column in Google Sheets

If you have hundreds of rows in a Google Spreadsheet and you want to apply the same formula to all rows of a particular column, there’s a more efficient solution than copy-paste - Array Formulas.
Highlight the first cell in the column and type the formula as earlier. However, instead of specifying a single cell as a parameter, we’ll specify the entire column using the B2:B notation (start from cell B2 and go all the way down to the last row of column B).
Then press Ctrl+Shift+Enter, or Cmd+Shift+Enter on Mac, and Google Sheets will automatically surround your formula with ARRAYFORMULA function.

Thus, we could apply the formula to the entire column of the spreadsheet with only a single cell. Array Formulas are more efficient as they process a batch of rows in one go. They are also easier to maintain as you only need to modify a single cell to edit the formula.
One issue that you may have noticed with the above formulae is that it applies to every row in the column where you have only want to add formulas to rows that contain data and skip the blank rows.
This can be done by adding an IF contain to our ARRAYFORMULA so that it doesn’t apply the formula the any of the blank rows.
Google Spreadsheet offers two functions to help test whether a cell is empty or now.
ISBLANK(A1) - Returns TRUE if the referenced cell is empty.
LEN(A1) <> 0 - Returns TRUE if the referenced cell not empty, FALSE otherwise
Our modified Array Formulas would therefore read:

## Using ISBLANK(Cell Reference):

There are several other ways to test if a cell is blank or not:

=ArrayFormula(IF(ISBLANK(B2:B), "", ROUND(B2:B*18%, 2)))
=ArrayFormula(IF(LEN(B2:B)<>0, ROUND(B2:B*18%, 2), ""))
=ArrayFormula(IF(B2:B="", "", ROUND(B2:B\*18%, 2)))

### Use Array Formulas inside Column Headers

In our previous examples, the text of the column titles (like Tax, Total Amount) was pre-populated and the formulas were only added to the first row of the dataset.
We can further improve our formula so that they can be applied to the column header itself. If the index of the current row is 1, calculated using the ROW() function, the formula outputs the column title else it performs the calculation using the formula.
=ArrayFormula(IF(ROW(B:B)=1,"Tax",IF(ISBLANK(B:B),"",ROUND(B:B\*18%, 2))))

### Auto Fill Formulas into Google Form Submissions

ARRAYFORMULA functions are particularly useful for Google Forms when the form responses are getting saved inside a Google Sheet. You cannot do live calculations inside Google Forms but they can be performed inside the spreadsheet that is collecting the responses.
You can create new columns inside the Google Spreadsheet and apply the ARRAYFORMULA to the first row of the added columns.
When a new form submission is received, a new row would be added to the Google Sheet and the formulas would be cloned and automatically applied to the new rows without you have to copy-paste stuff.

### How to Use VLOOKUP inside ARRAYFORMULA

You can combine ARRAYFORMULA with VLOOKUP to quickly perform a lookup across an entire column.
Say you have a “Fruits” sheet that lists the fruit names in column A and the corresponding prices in column B. The second sheet “Orders” has fruit names in column A, the quantity in column B and you are supposed to calculate the order amount in column C.

=ArrayFormula(
IF(ROW(A:A)=1,
"Total",
IF(NOT(ISBLANK(A:A)), VLOOKUP(A:A, Fruits!A2:B6, 2, FALSE) \* B:B, "")))

In simple English, if the row of the current cell is 1, output the column title in plain text. If the row is greater than 1 and the column A of the current row is not empty, perform a VLOOKUP to fetch the price of the item from the Fruits sheet. Then multiply that price with the quantity in cell B and output the value in cell C.
If your VLOOKUP range is in another Google Spreadsheet, use the IMPORTRANGE() function with the ID of the other Google Sheet.
Please note that you may have to use semicolons in the spreadsheet formulas instead of commas for some locales.