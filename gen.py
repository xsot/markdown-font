import fontforge

font = fontforge.open("fonts/SourceSans3-Regular.ttf")

all_glyphs = [font[i].glyphname for i in range(32, 127)]
# glyphs that do not need to be escaped in regular/bold/it/bold it contexts
simple_glyphs = all_glyphs[:]
simple_glyphs.remove('asterisk')
simple_glyphs.remove('backslash')

definitions = (''.join(
    f"@simple{suffix}=[{' '.join(glyph + suffix for glyph in simple_glyphs)}];\n"
    f"@all{suffix}=[{' '.join(glyph + suffix for glyph in all_glyphs)}];\n"
    for suffix in [''] + '.b .B .i .I .bi .BI .ib .a .BII .IBI'.split()) + 
    f"@all.m=[{' '.join(glyph + '.m' for glyph in all_glyphs)}];\n"
    f"@all.M=[{' '.join(glyph + '.M' for glyph in all_glyphs)}];\n")

remove_backslash = ''.join(
    f"    sub backslash.h {glyph}{suffix} by {glyph}{suffix};\n"
    for glyph in all_glyphs
    for suffix in [''] + ".b .i .bi .ib .a .m".split())

# glyphs that do not need to be escaped in mono contexts
mono_simple_glyphs = all_glyphs[:]
mono_simple_glyphs.remove('grave')
mono_simple_glyphs.remove('backslash')
prop_mono = f"sub [@all.m grave.om] [{' '.join(mono_simple_glyphs)}]' by [{' '.join(glyph + '.m' for glyph in mono_simple_glyphs)}];\n"

inner_remove_close = ''.join(
    f"    sub [{glyph}.a {glyph}.bi {glyph}.ib] asterisk.ca asterisk.ca asterisk.ca by {glyph}.BI;\n"
    f"    sub [{glyph}.a {glyph}.bi] asterisk.cbi by {glyph}.BII;\n"
    f"    sub [{glyph}.a {glyph}.ib] asterisk.cib asterisk.cib by {glyph}.IBI;\n"
    for glyph in all_glyphs)

outer_remove_close = ''.join(
    f"    sub {glyph}.b asterisk.cb asterisk.cb by {glyph}.B;\n"
    f"    sub {glyph}.i asterisk.ci by {glyph}.I;\n"
    f"    sub {glyph}.m grave.cm by {glyph}.M;\n"
    for glyph in all_glyphs)

inner_remove_open = ''.join(
    f"    sub asterisk.obi {glyph}.BII by {glyph}.BII;\n"
    f"    sub asterisk.oib asterisk.oib {glyph}.IBI by {glyph}.IBI;\n"
    # remove two oa if IB (bold inside)
    f"    sub asterisk.oa asterisk.oa {glyph}.IBI by {glyph}.IBI;\n"
    # remove one oa if BI (it inside)
    f"    sub asterisk.oa {glyph}.BII by {glyph}.BII;\n"
    # handle ac
    f"    sub asterisk.obi {glyph}.BI by {glyph}.BI;\n"
    f"    sub asterisk.oib asterisk.oib {glyph}.BI by {glyph}.BI;\n"
    for glyph in all_glyphs)

outer_remove_open = ''.join(
    f"sub asterisk.ob asterisk.ob {glyph}.B by {glyph}.B;\n"
    f"sub asterisk.oi {glyph}.I by {glyph}.I;\n"
    f"sub grave.om {glyph}.M by {glyph}.M;\n"
    # remove remaining oa
    f"sub asterisk.oa asterisk.oa asterisk.oa {glyph}.BI by {glyph}.BI;\n"
    f"sub asterisk.oa asterisk.oa {glyph}.BI by {glyph}.BI;\n"
    f"sub asterisk.oa {glyph}.BI by {glyph}.BI;\n"
    for glyph in all_glyphs)
    
print(f"""
languagesystem DFLT dflt;
languagesystem latn dflt;

{definitions}

lookup bold_to_reg1 {{ sub asterisk asterisk by asterisk.cb; }} bold_to_reg1;
lookup bold_to_reg2 {{ sub asterisk.cb by asterisk.cb asterisk.cb; }} bold_to_reg2;

lookup reg_to_bold1 {{ sub asterisk asterisk by asterisk.ob; }} reg_to_bold1;
lookup reg_to_bold2 {{ sub asterisk.ob by asterisk.ob asterisk.ob; }} reg_to_bold2;

lookup reg_to_all1 {{ sub asterisk asterisk asterisk by asterisk.oa; }} reg_to_all1;
lookup reg_to_all2 {{ sub asterisk.oa by asterisk.oa asterisk.oa asterisk.oa; }} reg_to_all2;

lookup all_to_reg1 {{ sub asterisk asterisk asterisk by asterisk.ca; }} all_to_reg1;
lookup all_to_reg2 {{ sub asterisk.ca by asterisk.ca asterisk.ca asterisk.ca; }} all_to_reg2;

lookup it_to_itbold1 {{ sub asterisk asterisk by asterisk.oib; }} it_to_itbold1;
lookup it_to_itbold2 {{ sub asterisk.oib by asterisk.oib asterisk.oib; }} it_to_itbold2;

lookup itbold_to_it1 {{ sub asterisk asterisk by asterisk.cib; }} itbold_to_it1;
lookup itbold_to_it2 {{ sub asterisk.cib by asterisk.cib asterisk.cib; }} itbold_to_it2;

lookup mark {{
    # escape/prop bold
    sub [@all.b asterisk.ob asterisk.cbi] backslash.h @all' by @all.b;
    sub [@all.b asterisk.ob asterisk.cbi] @simple' by @simple.b;

    # escape/prop it
    sub [@all.i asterisk.oi asterisk.cib] backslash.h @all' by @all.i;
    sub [@all.i asterisk.oi asterisk.cib] @simple' by @simple.i;

    # escape/prop boldit
    sub [@all.bi asterisk.obi] backslash.h @all' by @all.bi;
    sub [@all.bi asterisk.obi] @simple' by @simple.bi;

    # escape/prop itbold
    sub [@all.ib asterisk.oib] backslash.h @all' by @all.ib;
    sub [@all.ib asterisk.oib] @simple' by @simple.ib;

    # escape/prop all
    sub [@all.a asterisk.oa] backslash.h @all' by @all.a;
    sub [@all.a asterisk.oa] @simple' by @simple.a;

    # escape/prop mono
    sub [@all.m grave.om] backslash.h @all' by @all.m;
    {prop_mono}

    # escape regular
    ignore sub [asterisk.cb asterisk.ci asterisk.ca grave.cm] backslash.h [backslash asterisk grave]';
    ignore sub backslash.h [backslash asterisk grave]';

    # mark backslash
    sub backslash' by backslash.h;

    # *** all -> regular
    sub [@all.bi @all.ib @all.a] asterisk' lookup all_to_reg1 lookup all_to_reg2 asterisk' asterisk';

    # ** bold -> regular
    sub @all.b asterisk' lookup bold_to_reg1 lookup bold_to_reg2 asterisk';

    # ** it -> itbold
    sub @all.i asterisk' lookup it_to_itbold1 lookup it_to_itbold2 asterisk';

    # ** itbold/all -> it
    sub [@all.ib @all.a] asterisk' lookup itbold_to_it1 lookup itbold_to_it2 asterisk';

    # * bold -> boldit
    sub @all.b asterisk' by asterisk.obi;

    # * boldit/all -> bold
    sub [@all.bi @all.a] asterisk' by asterisk.cbi;

    # * it -> regular
    sub @all.i asterisk' by asterisk.ci;

    # *** regular -> all
    sub asterisk' lookup reg_to_all1 lookup reg_to_all2 asterisk' asterisk';

    # ** regular -> bold
    sub asterisk' lookup reg_to_bold1 lookup reg_to_bold2 asterisk';

    # * regular -> it
    sub asterisk' by asterisk.oi;

    # ` mono -> regular
    sub @all.m grave' by grave.cm;

    # ` regular -> mono
    sub grave' by grave.om;
}} mark;

lookup remove_backslash {{
{remove_backslash}
}} remove_backslash;

lookup inner_remove_close {{
{inner_remove_close}
}} inner_remove_close;

lookup inner_paint {{
    rsub @all.ib' @all.BII by @all.BII;
    rsub @all.bi' @all.BII by @all.BII;
    rsub @all.a' @all.BII by @all.BII;
    rsub @all.BII' @all.BII by @all.BII;

    rsub @all.ib' @all.IBI by @all.IBI;
    rsub @all.bi' @all.IBI by @all.IBI;
    rsub @all.a' @all.IBI by @all.IBI;
    rsub @all.IBI' @all.IBI by @all.IBI;

    # handle ac
    rsub @all.ib' @all.BI by @all.BI;
    rsub @all.bi' @all.BI by @all.BI;
    rsub @all.a' @all.BI by @all.BI;
}} inner_paint;

lookup inner_remove_open {{
{inner_remove_open}
}} inner_remove_open;

lookup outer_remove_close {{
{outer_remove_close}
}} outer_remove_close;

lookup outer_paint {{
    rsub @all.b' [@all.B @all.BI] by @all.B;
    rsub @all.i' [@all.I @all.BI] by @all.I;
    rsub @all.m' @all.M by @all.M;
    rsub @all.BII' @all.BI by @all.BI;
    rsub @all.BII' [@all.I @all.B] by @all.BI;
    rsub @all.IBI' @all.BI by @all.BI;
    rsub @all.IBI' [@all.I @all.B] by @all.BI;
}} outer_paint;

lookup outer_remove_open {{
{outer_remove_open}
}} outer_remove_open;

feature calt {{
    lookup mark;

    lookup remove_backslash;
    lookup inner_remove_close;
    lookup inner_paint;
    lookup inner_remove_open;
    lookup outer_remove_close;
    lookup outer_paint;
    lookup outer_remove_open;
}} calt;
""")
