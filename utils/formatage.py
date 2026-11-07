def fcfa(valeur):
    if valeur is None:
        return "Non disponible"
    return f"{valeur:,.0f}".replace(",", " ") + " FCFA"

def pourcentage(valeur):
    return "Non calculable" if valeur is None else f"{valeur:.2f} %"
