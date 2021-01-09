import fontforge
import psMat
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeatures

font = fontforge.open("fonts/SourceSerifPro-Regular.ttf")
it = fontforge.open("fonts/SourceSerifPro-It.ttf")
bold = fontforge.open("fonts/SourceSerifPro-Bold.ttf")
boldit = fontforge.open("fonts/SourceSerifPro-BoldIt.ttf")
mono = fontforge.open("fonts/iosevka-regular.ttf")
eager = True

# clobber the private use area
codepoint = 0xe000

# copy a glyph and all referenced glyphs
# new glyphs are renamed with a suffix
def deepcopy_glyph(src_font, src_codepoint, suffix):
    global codepoint
    global font
    root_codepoint = codepoint
    src_font.selection.select(src_codepoint)
    src_font.copy()
    font.selection.select(codepoint)
    font.paste()
    glyph = font[codepoint]
    glyph.glyphname = src_font[src_codepoint].glyphname + suffix
    codepoint += 1
    if src_font[src_codepoint].references:
        renamed_refs = []
        for ref in src_font[src_codepoint].references:
            src_font.selection.select(ref[0])
            src_font.copy()
            font.selection.select(codepoint)
            font.paste() # for some reason, this doesn't preserve the width of certain glyphs in source code pro
            glyph = font[codepoint]
            glyph.glyphname = src_font[ref[0]].glyphname + suffix
            renamed_refs.append((glyph.glyphname, ref[1]))
            codepoint += 1
        font[root_codepoint].references = tuple(renamed_refs)

for i in range(32, 127):
    # partial bold
    deepcopy_glyph(bold if eager else font, i, ".b")
    # bold
    deepcopy_glyph(bold, i, ".B")
    # partial it
    deepcopy_glyph(it if eager else font, i, ".i")
    # it
    deepcopy_glyph(it, i, ".I")
    # partial mono
    deepcopy_glyph(mono if eager else font, i, ".m")
    # mono
    deepcopy_glyph(mono, i, ".M")
    # partial boldit
    deepcopy_glyph(boldit if eager else font, i, ".bi")
    # partial it bold
    deepcopy_glyph(boldit if eager else font, i, ".ib")
    # partial all (boldit where order doesn't matter)
    deepcopy_glyph(boldit if eager else font, i, ".a")
    # bold it
    deepcopy_glyph(boldit, i, ".BI")
    # bold it inside
    deepcopy_glyph(boldit if eager else it, i, ".BII")
    # it bold inside
    deepcopy_glyph(boldit if eager else bold, i, ".IBI")

# open/close bold 
deepcopy_glyph(font, ord('*'), ".ob")
deepcopy_glyph(font, ord('*'), ".cb")
# open/close it 
deepcopy_glyph(font, ord('*'), ".oi")
deepcopy_glyph(font, ord('*'), ".ci")
# open/close mono 
deepcopy_glyph(font, ord('`'), ".om")
deepcopy_glyph(font, ord('`'), ".cm")
# open/close boldit
deepcopy_glyph(font, ord('*'), ".obi")
deepcopy_glyph(font, ord('*'), ".cbi")
# open/close itbold
deepcopy_glyph(font, ord('*'), ".oib")
deepcopy_glyph(font, ord('*'), ".cib")
# open/close all
deepcopy_glyph(font, ord('*'), ".oa")
deepcopy_glyph(font, ord('*'), ".ca")
# hidden
deepcopy_glyph(font, ord('\\'), ".h")

font.generate('tmp.ttf')

font.close()
it.close()
bold.close()
boldit.close()
mono.close()

ft_font = TTFont('tmp.ttf')
addOpenTypeFeatures(ft_font, 'md.fea', tables=['GSUB'])
ft_font.save('fonts/output.ttf')
