🌍 Real IP Locator & Geolocalizer

Ferramenta de inteligência de rede que identifica o IP público real de um alvo (domínio ou IP) e extrai sua geolocalização física, detalhes do ISP e informações de rede em tempo real.

O objetivo principal é diferenciar IPs de origem física de IPs atrás de CDNs (como Cloudflare ou Akamai) e fornecer um relatório detalhado com coordenadas geográficas, ASN e provedor de internet.

## ✨ Funcionalidades

*   **Resolução Inteligente:** Aceita domínios (`exemplo.com`) ou IPs diretos (`192.168.1.1`).
*   **Detecção de CDN/Proxy:** Identifica automaticamente se o IP pertence a um CDN conhecido (Cloudflare, Akamai, Google, etc.) e alerta que a localização pode ser de um PoP (Point of Presence).
*   **Geolocalização Precisa:** Obtém latitude, longitude, cidade, região e fuso horário via API `ip-api.com`.
*   **Inteligência de Rede (Threat Intel):**
    *   Consulta ao RIPEstat para obter o prefixo de rede.
    *   Identificação de ASN (Autonomous System Number) e Nome do ASN.
    *   Identificação do ISP (Operador de Telecomunicações) e Organização.
*   **Reverse DNS (PTR):** Recupera nomes de host reversos associados ao IP.
*   **Relatório Automático:** Gera um relatório no terminal e salva os dados em um arquivo `JSON`.
*   **Mapa Interativo:** Gera um arquivo HTML com um mapa visual da localização usando a biblioteca `Folium`.

## 📦 Dependências

O projeto requer Python 3.7+.

As seguintes bibliotecas são necessárias:
*   `requests`: Para comunicação com APIs externas.
*   `folium`: Para geração do mapa interativo HTML.

### Instalação

Abra o terminal e execute:

```bash
pip install requests folium
🚀 Como Usar
Execute o script principal:

bash
Download
Copy code
python real_ip_locator.py
Será solicitado que você insira o IP ou domínio do alvo.

Exemplo de Saída no Terminal
text
Download
Copy code
Iniciando análise para: google.com
[INFO] Domínio google.com resolvido para: 104.21.5.12

==================================================
RELATÓRIO DE LOCALIZAÇÃO EM TEMPO REAL
Alvo: google.com
IP Real: 104.21.5.12
==================================================

--- IDENTIDADE DE REDE ---
Hosts Reversos (PTR): 104.21.5.12

--- GEOLOCALIZAÇÃO ---
País: United States
Região: California
Cidade: San Francisco
CEP: 94107
Coordenadas: 37.7749, -122.4194
Fuso Horário: America/Los_Angeles

--- DETALHES DO ISP/ASN ---
Provedor (ISP): Cloudflare, Inc.
Organização: Cloudflare, Inc.
ASN: AS13335
Nome ASN: CLOUDFLARENET

[ALERTA] O IP 104.21.5.12 pertence a Cloudflare. A localização geográfica reflete o PoP (Point of Presence) do CDN, não necessariamente a localização física do servidor final.

[INFO] O IP não pertence a um ASN de CDN conhecido. A localização provavelmente é mais precisa.

Relatório salvo em 'location_report.json'
[INFO] Mapa interativo gerado em: location_map.html
================================================