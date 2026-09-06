# --- FUNÇÃO DE BUSCA NA TABELA ANP (NBR 5992) ---
def buscar_inpm_na_tabela(dens_20):
    # Tabela com os valores de Densidade a 20°C (g/mL) correspondentes aos °INPM
    tabela_inpm = {
        0.8113: 92.5, 0.8110: 92.6, 0.8107: 92.7, 0.8104: 92.8, 0.8101: 92.9,
        0.8098: 93.0, 0.8094: 93.1, 0.8091: 93.2, 0.8088: 93.3, 0.8085: 93.4,
        0.8082: 93.5, 0.8079: 93.6, 0.8076: 93.7, 0.8072: 93.8, 0.8069: 93.9,
        0.8066: 94.0, 0.8063: 94.1, 0.8060: 94.2, 0.8057: 94.3, 0.8053: 94.4,
        0.8050: 94.5, 0.8047: 94.6, 0.8044: 94.7, 0.8041: 94.8, 0.8038: 94.9,
        0.8035: 95.0, 0.8031: 95.1, 0.8028: 95.2, 0.8025: 95.3, 0.8022: 95.4
    }
    # Encontra a densidade mais próxima na tabela para evitar erros de arredondamento
    dens_proxima = min(tabela_inpm.keys(), key=lambda k: abs(k - dens_20))
    return tabela_inpm[dens_proxima]
