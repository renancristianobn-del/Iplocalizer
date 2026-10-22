import socket
import requests
import ipaddress
import folium
from typing import Dict, List, Optional

def show_banner() -> None:
    print(
        """
████████╗ ██████╗ ██╗  ██╗██╗   ██╗ ██████╗  ██████╗
╚══██╔══╝██╔═══██╗██║ ██╔╝╚██╗ ██╔╝██╔═══██╗██╔═══██╗
   ██║   ██║   ██║█████╔╝  ╚████╔╝ ██║   ██║██║   ██║
   ██║   ██║   ██║██╔═██╗   ╚██╔╝  ██║   ██║██║   ██║
   ██║   ╚██████╔╝██║  ██╗   ██║   ╚██████╔╝╚██████╔╝
   ╚═╝    ╚═════╝  ╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝

              iplocalizer v1.1
              Made by Tokyoo
"""
    )

class RealIPLocator:
    # Dentro da classe RealIPLocator, adicione este método:
    def generate_map(self, filename: str = "location_map.html") -> None:
        """
        Gera um mapa HTML interativo usando folium.
        """
        if not self.location_data:
            print("[AVISO] Sem dados de geolocalização para gerar o mapa.")
            return

        lat = self.location_data.get('lat')
        lon = self.location_data.get('lon')
        
        # Verifica se as coordenadas são válidas (não None ou 0,0)
        if lat is None or lon is None or (lat == 0 and lon == 0):
            print("[AVISO] Coordenadas inválidas ou ausentes.")
            return

        # Cria o mapa centrado na localização
        m = folium.Map(location=[lat, lon], zoom_start=15)

        # Adiciona um marcador com informações do alvo
        popup_html = f"""
        <b>Alvo:</b> {self.target}<br>
        <b>IP Real:</b> {self.resolved_ip}<br>
        <b>Cidade:</b> {self.location_data.get('city', 'N/A')}<br>
        <b>Região:</b> {self.location_data.get('regionName', 'N/A')}<br>
        <b>País:</b> {self.location_data.get('country', 'N/A')}<br>
        <b>ISP:</b> {self.location_data.get('isp', 'N/A')}
        """
        
        folium.Popup(popup_html, max_width=300).add_to(m)
        
        # Adiciona um marcador visual
        folium.Marker(
            location=[lat, lon],
            icon=folium.Icon(color='red', icon='server', icon_color='white')
        ).add_to(m)
    """
    Classe para localizar o IP real de um alvo e extrair sua geolocalização.
    """
    def __init__(self, target: str):
        self.target = target
        self.resolved_ip: Optional[str] = None
        self.location_data: Optional[Dict] = None
        self.network_info: Optional[Dict] = None

    def resolve_target(self) -> Optional[str]:
        """
        Resolve o nome de domínio para o IP.
        Se o alvo já for um IP, retorna-o diretamente.
        """
        # Primeiro, tenta validar se é um IP válido
        try:
            ipaddress.ip_address(self.target)
            # Se não lançar exceção, é um IP válido
            self.resolved_ip = self.target
            print(f"[INFO] Alvo identificado como IP direto: {self.resolved_ip}")
            return self.resolved_ip
        except ValueError:
            # Se lançar ValueError, é um domínio (ou string inválida)
            pass

        # Se não for IP, tenta resolver como domínio
        try:
            ip = socket.gethostbyname(self.target)
            self.resolved_ip = ip
            print(f"[INFO] Domínio {self.target} resolvido para: {self.resolved_ip}")
            return self.resolved_ip
        except socket.gaierror as e:
            print(f"[ERRO] Não foi possível resolver {self.target}. Detalhe: {e}")
            return None
    def get_reverse_dns(self) -> List[str]:
        """
        Obtém os nomes de host reversos (PTR records) associados ao IP.
        """
        try:
            names = socket.gethostbyaddr(self.resolved_ip)
            # names[0] é o nome principal, names[1:] são os aliases
            return [names[0]] + list(names[1:])
        except socket.herror:
            return []

    def query_ip_api(self) -> Optional[Dict]:
        """
        Consulta a API ip-api.com (gratuita) para obter geolocalização e 
        detalhes da rede (ASN, ISP, etc.).
        """
        if not self.resolved_ip:
            return None
        
        url = f"http://ip-api.com/json/{self.resolved_ip}?fields=status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,query"
        
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            if data.get('status') == 'success':
                self.location_data = data
                return data
            else:
                print(f"[AVISO] API retornou: {data.get('message')}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"[ERRO] Falha na consulta da API: {e}")
            return None

    def query_bgp_tools(self) -> Optional[Dict]:
        """
        Consulta o BGPTools (via API pública ou scraping simples) para obter 
        informações mais profundas sobre a rede (prefixo, ISP).
        """
        # Para fins de simplicidade, usaremos a API do ip-api que já fornece 
        # informações de ASN e ISP. Em um projeto real, você poderia usar 
        # o bgp.he.net ou o RIPEstat para dados mais precisos sobre o 
        # "prefixo" do roteador.
        
        # Exemplo de como usar o RIPEstat para verificar o prefixo:
        if not self.resolved_ip:
            return None
            
        try:
            # RIPEstat API para obter o prefixo
            ripestat_url = f"https://stat.ripe.net/data/network-info/data.json?resource={self.resolved_ip}"
            response = requests.get(ripestat_url, timeout=5)
            data = response.json()
            if data.get('code') == 200:
                self.network_info = data.get('data', {})
                return self.network_info
        except requests.exceptions.RequestException:
            pass
        return None

    def analyze_cdn_proxy(self) -> bool:
        """
        Analisa se o IP pertence a um CDN conhecido (Cloudflare, Akamai, etc.)
        usando a lista de ASNs conhecidos.
        """
        if not self.location_data:
            return False
            
        asn = self.location_data.get('as', '')
        # Lista simplificada de ASNs de CDNs/Proxies
        cdn_asns = {
            'AS13335': 'Cloudflare',
            'AS16509': 'AKAMAI-AS',
            'AS15169': 'GOOGLE',
            'AS16549': 'CHARTER', # Frequentemente usado em CDNs
            'AS8075': 'MICROSOFT-CORP-MSN-AS-BLOCK'
        }
        
        if asn in cdn_asns:
            print(f"[INFO] O IP {self.resolved_ip} pertence a {cdn_asns[asn]}.")
            return True
        return False

    def generate_report(self) -> str:
        """
        Gera um relatório detalhado da localização e identidade do alvo.
        """
        if not self.resolved_ip:
            return "Falha ao resolver o alvo."
        
        report = f"""
        ==================================================
        RELATÓRIO DE LOCALIZAÇÃO EM TEMPO REAL
        Alvo: {self.target}
        IP Real: {self.resolved_ip}
        ==================================================
        
        --- IDENTIDADE DE REDE ---
        """
        
        # Reverse DNS
        rdn = self.get_reverse_dns()
        if rdn:
            report += f"Hosts Reversos (PTR): {', '.join(rdn[:3])}\n"
        
        # Geolocalização
        if self.location_data:
            report += f"""
        --- GEOLOCALIZAÇÃO ---
        País: {self.location_data.get('country')}
        Região: {self.location_data.get('regionName')}
        Cidade: {self.location_data.get('city')}
        CEP: {self.location_data.get('zip')}
        Coordenadas: {self.location_data.get('lat')}, {self.location_data.get('lon')}
        Fuso Horário: {self.location_data.get('timezone')}
        """
        
        # Detalhes do ISP/ASN
        report += f"""
        --- DETALHES DO ISP/ASN ---
        Provedor (ISP): {self.location_data.get('isp')}
        Organização: {self.location_data.get('org')}
        ASN: {self.location_data.get('as')}
        Nome ASN: {self.location_data.get('asname')}
        """
        
        # Análise de CDN
        if self.analyze_cdn_proxy():
            report += "\n[ALERTA] O IP está atrás de um CDN/Proxy. A localização geográfica reflete o PoP (Point of Presence) do CDN, não necessariamente a localização física do servidor final.\n"
        else:
            report += "\n[INFO] O IP não pertence a um ASN de CDN conhecido. A localização provavelmente é mais precisa.\n"
        
        # Informações do Prefixo (RIPEstat)
        if self.network_info:
            prefix_info = self.network_info.get('prefix', 'N/A')
            report += f"Prefixo de Rede (RIPEstat): {prefix_info}\n"
            
        report += "\n================================================\n"
        return report

    def generate_map(self):
        """
        Gera um mapa interativo da localização do IP.
        """
        if not self.location_data:
            print("Nenhuma informação de localização disponível para gerar o mapa.")
            return

        lat = self.location_data.get('lat')
        lon = self.location_data.get('lon')

        if not lat or not lon:
            print("Coordenadas geográficas não disponíveis.")
            return

        # Criar o mapa
        m = folium.Map(location=[lat, lon], zoom_start=10)

        # Adicionar marcador
        folium.Marker(
            location=[lat, lon],
            popup=f"IP: {self.resolved_ip}<br>Localização: {self.location_data.get('city')}, {self.location_data.get('country')}"
        ).add_to(m)

        # Salvar o mapa
        m.save("location_map.html")
        print("Mapa interativo salvo em 'location_map.html'")

    def run(self):
        """
        Executa o fluxo completo de localização.
        """
        print(f"Iniciando análise para: {self.target}")
        
        # 1. Resolver IP
        if not self.resolve_target():
            return
        
        # 2. Consultar APIs
        self.query_ip_api()
        self.query_bgp_tools()
        
        # 3. Gerar Relatório
        report = self.generate_report()
        print(report)
        
        # 4. Gerar Mapa Interativo
        self.generate_map()

# Exemplo de uso
if __name__ == "__main__":
    show_banner()
    # Substitua pelo IP ou domínio do seu alvo
    target = input("Digite o IP ou domínio do alvo: ")
    locator = RealIPLocator(target)
    locator.run()