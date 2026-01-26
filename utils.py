# utils.py
# Full Fonts Pack for BAKA Bot

class Fonts:

    @staticmethod
    def _apply(text, mapping):
        for a, b in mapping.items():
            text = text.replace(a, b)
        return text

    # ================= BASIC =================

    @staticmethod
    def typewriter(text):
        return Fonts._apply(text, {
            "a":"𝚊","b":"𝚋","c":"𝚌","d":"𝚍","e":"𝚎","f":"𝚏","g":"𝚐","h":"𝚑","i":"𝚒","j":"𝚓","k":"𝚔","l":"𝚕","m":"𝚖","n":"𝚗","o":"𝚘","p":"𝚙","q":"𝚚","r":"𝚛","s":"𝚜","t":"𝚝","u":"𝚞","v":"𝚟","w":"𝚠","x":"𝚡","y":"𝚢","z":"𝚣",
            "A":"𝙰","B":"𝙱","C":"𝙲","D":"𝙳","E":"𝙴","F":"𝙵","G":"𝙶","H":"𝙷","I":"𝙸","J":"𝙹","K":"𝙺","L":"𝙻","M":"𝙼","N":"𝙽","O":"𝙾","P":"𝙿","Q":"𝚀","R":"𝚁","S":"𝚂","T":"𝚃","U":"𝚄","V":"𝚅","W":"𝚆","X":"𝚇","Y":"𝚈","Z":"𝚉"
        })

    @staticmethod
    def outline(text):
        return Fonts._apply(text, {
            "a":"𝕒","b":"𝕓","c":"𝕔","d":"𝕕","e":"𝕖","f":"𝕗","g":"𝕘","h":"𝕙","i":"𝕚","j":"𝕛","k":"𝕜","l":"𝕝","m":"𝕞","n":"𝕟","o":"𝕠","p":"𝕡","q":"𝕢","r":"𝕣","s":"𝕤","t":"𝕥","u":"𝕦","v":"𝕧","w":"𝕨","x":"𝕩","y":"𝕪","z":"𝕫",
            "A":"𝔸","B":"𝔹","C":"ℂ","D":"𝔻","E":"𝔼","F":"𝔽","G":"𝔾","H":"ℍ","I":"𝕀","J":"𝕁","K":"𝕂","L":"𝕃","M":"𝕄","N":"ℕ","O":"𝕆","P":"ℙ","Q":"ℚ","R":"ℝ","S":"𝕊","T":"𝕋","U":"𝕌","V":"𝕍","W":"𝕎","X":"𝕏","Y":"𝕐","Z":"ℤ"
        })

    @staticmethod
    def bold(text):
        return Fonts._apply(text, {
            "a":"𝐚","b":"𝐛","c":"𝐜","d":"𝐝","e":"𝐞","f":"𝐟","g":"𝐠","h":"𝐡","i":"𝐢","j":"𝐣","k":"𝐤","l":"𝐥","m":"𝐦","n":"𝐧","o":"𝐨","p":"𝐩","q":"𝐪","r":"𝐫","s":"𝐬","t":"𝐭","u":"𝐮","v":"𝐯","w":"𝐰","x":"𝐱","y":"𝐲","z":"𝐳",
            "A":"𝐀","B":"𝐁","C":"𝐂","D":"𝐃","E":"𝐄","F":"𝐅","G":"𝐆","H":"𝐇","I":"𝐈","J":"𝐉","K":"𝐊","L":"𝐋","M":"𝐌","N":"𝐍","O":"𝐎","P":"𝐏","Q":"𝐐","R":"𝐑","S":"𝐒","T":"𝐓","U":"𝐔","V":"𝐕","W":"𝐖","X":"𝐗","Y":"𝐘","Z":"𝐙"
        })

    @staticmethod
    def smallcap(text):
        return Fonts._apply(text, {
            "a":"ᴀ","b":"ʙ","c":"ᴄ","d":"ᴅ","e":"ᴇ","f":"ғ","g":"ɢ","h":"ʜ","i":"ɪ","j":"ᴊ","k":"ᴋ","l":"ʟ","m":"ᴍ","n":"ɴ","o":"ᴏ","p":"ᴘ","q":"ǫ","r":"ʀ","s":"s","t":"ᴛ","u":"ᴜ","v":"ᴠ","w":"ᴡ","x":"x","y":"ʏ","z":"ᴢ"
        })

    # ================= FUN =================

    @staticmethod
    def circles(text):
        return Fonts._apply(text, {
            "a":"ⓐ","b":"ⓑ","c":"ⓒ","d":"ⓓ","e":"ⓔ","f":"ⓕ","g":"ⓖ","h":"ⓗ","i":"ⓘ","j":"ⓙ","k":"ⓚ","l":"ⓛ","m":"ⓜ","n":"ⓝ","o":"ⓞ","p":"ⓟ","q":"ⓠ","r":"ⓡ","s":"ⓢ","t":"ⓣ","u":"ⓤ","v":"ⓥ","w":"ⓦ","x":"ⓧ","y":"ⓨ","z":"ⓩ",
            "A":"Ⓐ","B":"Ⓑ","C":"Ⓒ","D":"Ⓓ","E":"Ⓔ","F":"Ⓕ","G":"Ⓖ","H":"Ⓗ","I":"Ⓘ","J":"Ⓙ","K":"Ⓚ","L":"Ⓛ","M":"Ⓜ","N":"Ⓝ","O":"Ⓞ","P":"Ⓟ","Q":"Ⓠ","R":"Ⓡ","S":"Ⓢ","T":"Ⓣ","U":"Ⓤ","V":"Ⓥ","W":"Ⓦ","X":"Ⓧ","Y":"Ⓨ","Z":"Ⓩ"
        })

    @staticmethod
    def dark_circle(text):
        return Fonts._apply(text, {
            "a":"🅐","b":"🅑","c":"🅒","d":"🅓","e":"🅔","f":"🅕","g":"🅖","h":"🅗","i":"🅘","j":"🅙","k":"🅚","l":"🅛","m":"🅜","n":"🅝","o":"🅞","p":"🅟","q":"🅠","r":"🅡","s":"🅢","t":"🅣","u":"🅤","v":"🅥","w":"🅦","x":"🅧","y":"🅨","z":"🅩",
        })

    @staticmethod
    def bubbles(text):
        return Fonts._apply(text, {
            "a":"⒜","b":"⒝","c":"⒞","d":"⒟","e":"⒠","f":"⒡","g":"⒢","h":"⒣","i":"⒤","j":"⒥","k":"⒦","l":"⒧","m":"⒨","n":"⒩","o":"⒪","p":"⒫","q":"⒬","r":"⒭","s":"⒮","t":"⒯","u":"⒰","v":"⒱","w":"⒲","x":"⒳","y":"⒴","z":"⒵"
        })

    @staticmethod
    def strike(text):
        return "".join([c + "̶" for c in text])

    @staticmethod
    def underline(text):
        return "".join([c + "͟" for c in text])

    @staticmethod
    def frozen(text):
        return "".join([c + "༙" for c in text])

    @staticmethod
    def slash(text):
        return "".join([c + "̸" for c in text])

    @staticmethod
    def clouds(text):
        return "".join([c + "͜͡" for c in text])

    @staticmethod
    def arrows(text):
        return "".join([c + "͎" for c in text])

    @staticmethod
    def skyline(text):
        return "".join([c + "̺͆" for c in text])

    @staticmethod
    def rays(text):
        return "".join([c + "҉" for c in text])

    @staticmethod
    def birds(text):
        return "".join([c + "҈" for c in text])

    @staticmethod
    def stop(text):
        return "".join([c + "⃠" for c in text])

    @staticmethod
    def sad(text):
        return "".join([c + "̑̈" for c in text])

    @staticmethod
    def happy(text):
        return "".join([c + "̆̈" for c in text])
