# Kysely – paikallinen, puhuva tekoälykysely

Kysely on selaimessa toimiva suomenkielinen keskustelusivu. Kysymyksen voi
kirjoittaa tai sanella mikrofonilla, ja tekoälyn vastaus voidaan lukea ääneen.
Tekoälyvastaukset tuotetaan omalla tietokoneella Ollamalla; niiden luomiseen ei
tarvita pilven tekoälypalvelua.

## Sisällys

- [Toiminta ja komponentit](#toiminta-ja-komponentit)
- [Asennettavat ohjelmat ja vaatimukset](#asennettavat-ohjelmat-ja-vaatimukset)
- [Asennus ja käynnistys Windowsissa](#asennus-ja-käynnistys-windowsissa)
- [Käyttö](#käyttö)
- [Tietosuoja ja äänen käsittely](#tietosuoja-ja-äänen-käsittely)
- [Tavalliset ongelmat](#tavalliset-ongelmat)
- [Opettajan ohje: rakenna vastaava sovellus prompteilla](#opettajan-ohje-rakenna-vastaava-sovellus-prompteilla)

## Toiminta ja komponentit

Sovelluksessa on kolme pääosaa:

1. **Selainkäyttöliittymä – `index.html`.** HTML muodostaa keskustelun,
   tekstikentän, mikrofonin ja mallivalitsimen. CSS tyylittelee sivun ja avatarin.
   Sivun JavaScript lähettää kysymykset paikalliselle Python-palvelimelle,
   näyttää vastaukset ja säilyttää keskusteluhistorian sivun aukiolon ajan.
2. **Paikallinen välityspalvelin – `app.py`.** Pythonin vakiokirjaston
   `http.server` tarjoaa sivun ja kolme rajapintaa:
   - `GET /api/models` hakee asennettujen mallien nimet Ollamalta.
   - `POST /api/load` pyytää valitun mallin lataamista muistiin.
   - `POST /api/chat` lähettää keskustelun Ollaman chat-rajapintaan ja palauttaa
     tekoälyn vastauksen selaimelle.

   Palvelin kuuntelee vain tämän tietokoneen osoitteessa `127.0.0.1:8000`.
   Se tarkistaa syötteen ja sallii enintään 1 000 000 tavun HTTP-pyynnön.
3. **Paikallinen kielimalli – Ollama.** Oletusmalli on
   `jobautomation/OpenEuroLLM-Finnish:latest`. Selaimen mallivalikossa voi
   käyttää myös muita koneelle Ollamalla asennettuja malleja. Vastausta varten
   selaimelta palvelimelle lähetetään keskusteluhistoria; palvelin välittää sen
   valitulle mallille.

### Puhe ja mikrofoni

- **Puheeksi muuttaminen (tekoälyn vastaus ääneen):** selain lukee vastauksen
  `speechSynthesis`-rajapinnalla. Suomenkielisen äänen saatavuus ja laatu
  riippuvat selaimesta ja käyttöjärjestelmään asennetuista äänistä.
- **Puheentunnistus (mikrofoni):** selain tunnistaa suomeksi puhutun kysymyksen
  `SpeechRecognition`- tai `webkitSpeechRecognition`-rajapinnalla ja lisää
  tunnistetun tekstin kysymyskenttään. Käyttäjä lähettää kysymyksen tämän jälkeen
  itse.
- **Avatar:** SVG-hahmo vaihtaa suun animaatiota selaimen puhesynteesin ajaksi.
  Animaatio ei luo ääntä; äänen tuottaa selaimen puhesynteesi.

## Asennettavat ohjelmat ja vaatimukset

- **Python 3** (suositus Python 3.10 tai uudempi). Sovellus käyttää vain
  Pythonin vakiokirjastoa; `pip install` -asennuksia ei tarvita.
- **Ollama** Windowsille: <https://ollama.com/download>
- **Ollama-malli:** oletusmalli tai muu koneen resursseihin sopiva, Ollaman
  tukema chat-malli.
- **Puheominaisuudet sisältävä selain.** Microsoft Edge tai Google Chrome on
  suositeltava. Suomenkielinen puhesynteesi ja mikrofonin puheentunnistus ovat
  selaimen ominaisuuksia, eivät Ollaman ominaisuuksia.
- **Muistia ja levytilaa mallille.** Kielimallit voivat olla suuria ja niiden
  nopeus riippuu koneen suorittimesta, muistista ja näytönohjaimesta. Tarkista
  mallin omat laitteistovaatimukset ennen latausta.

## Asennus ja käynnistys Windowsissa

### 1. Asenna ja tarkista Ollama

Asenna Ollama yllä olevasta osoitteesta. Avaa PowerShell ja tarkista, että
komento toimii:

```powershell
ollama --version
```

Lataa oletusmalli:

```powershell
ollama pull jobautomation/OpenEuroLLM-Finnish:latest
```

Mallin lataaminen voi kestää ja vaatii verkkoyhteyden. Kun malli ja ohjelmat on
asennettu, kyselyiden generointi toimii paikallisesti. Tarkista asennetut mallit
komennolla:

```powershell
ollama list
```

Ollaman pitää olla käynnissä kyselysovelluksen käytön aikana. Windowsissa
Ollama käynnistyy yleensä asennuksen jälkeen taustalle. Jos sovellus ei saa
yhteyttä siihen, avaa Ollama-sovellus Käynnistä-valikosta.

### 2. Käynnistä kyselypalvelin

Avaa PowerShell projektin kansiossa, eli kansiossa, jossa `app.py` sijaitsee.
Esimerkiksi:

```powershell
cd C:\polku\kysely
python app.py
```

Jos `python`-komento ei löydy mutta Python Launcher on asennettu, kokeile:

```powershell
py app.py
```

Pidä tämä terminaali-ikkuna auki sovelluksen käytön ajan. Palvelimen
käynnistyessä terminaali näyttää osoitteet `http://localhost:8000` ja
`http://127.0.0.1:8000`.

### 3. Avaa kysely

Avaa selaimessa <http://localhost:8000>. Älä sulje palvelimen terminaali-ikkunaa
keskustelun aikana. Sovellus ei vaadi Node.js:ää, npm:ää, tietokantaa,
virtuaaliympäristöä eikä Python-pakettien asennusta.

## Käyttö

1. Varmista, että Ollama ja `python app.py` ovat käynnissä.
2. Avaa <http://localhost:8000>.
3. Valitse oikean yläkulman luettelosta asennettu malli. Valinta tallentuu
   selaimen paikalliseen tallennustilaan ja malli ladataan muistiin.
4. Kirjoita kysymys tai valitse mikrofonipainike, anna selaimelle mikrofonilupa
   ja sanele kysymys suomeksi. Tunnistettu teksti tulee tekstikenttään.
5. Lähetä kysymys nuolipainikkeella tai Enter-näppäimellä. Shift + Enter tekee
   rivinvaihdon. Syötteen enimmäispituus on 4 000 merkkiä.
6. Tekoälyn vastaus näkyy keskustelussa ja luetaan ääneen, jos selaimen
   puhesynteesi on tuettu ja ääni on päällä. Äänen voi mykistää ja käynnissä
   olevan puheen keskeyttää; äänen voi ottaa takaisin käyttöön tulevia
   vastauksia varten.

Mikrofoni ja äänilähtö ovat toisistaan erillisiä: kirjoitettukin kysymys
voidaan lukea ääneen, eikä mikrofonia tarvita tekstikysymyksiin.

## Tietosuoja ja äänen käsittely

Kysymysteksti ja keskusteluhistoria lähetetään paikalliseen palvelimeen
(`127.0.0.1:8000`), joka välittää ne paikalliselle Ollamalle
(`127.0.0.1:11434`). Tekoälyvastaus luodaan omalla koneella. Sovellus ei
itsessään tallenna keskusteluhistoriaa levylle; selaimen JavaScript pitää sen
muistissa sivun aukiolon ajan.

**Mikrofonin puheentunnistus ei välttämättä ole paikallinen.** Selain voi
lähettää puheäänen tai puheentunnistuspyynnön selaimen tarjoamaan
verkkopalveluun. Tämä riippuu selaimesta ja sen asetuksista. Kerro tästä
käyttäjille ennen mikrofonin käyttöä ja tutustu käyttämäsi selaimen
tietosuojakäytäntöön. Mikrofonilupa pyydetään selaimelta; sovellus ei tallenna
äänitallennetta.

Puhesynteesi tapahtuu selaimen ja käyttöjärjestelmän puhepalveluilla.
Verkkosivulla ei käytetä ulkoisia JavaScript-kirjastoja, CDN-palveluja tai
tekoäly-API-avaimia.

## Tavalliset ongelmat

- **Sivu ei avaudu tai kysymykseen ei tule vastausta:** tarkista, että
  `python app.py` on edelleen käynnissä ja selaimen osoite on
  `http://localhost:8000`.
- **Ollamaan ei saada yhteyttä:** käynnistä Ollama uudelleen ja kokeile
  PowerShellissä `ollama list`.
- **Mallia ei löydy:** suorita
  `ollama pull jobautomation/OpenEuroLLM-Finnish:latest`, odota latauksen
  valmistumista ja päivitä sivu.
- **Vastaukset ovat hitaita:** kokeile koneelle sopivampaa tai pienempää
  Ollama-mallia. Mallivalikko näyttää Ollaman ilmoittamat asennetut mallit.
- **Mikrofoni ei toimi:** tarkista selaimen sivustokohtainen mikrofonilupa,
  käyttöjärjestelmän mikrofoniasetukset ja että mikrofoni ei ole toisen
  sovelluksen käytössä. Puheentunnistus ei ole kaikissa selaimissa tuettu.
- **Suomenkielinen ääni puuttuu tai kuulostaa huonolta:** puheäänen valikoima
  määräytyy selaimen ja käyttöjärjestelmän mukaan. Asenna niihin suomenkielinen
  ääni tai kokeile Edgeä.

## Opettajan ohje: rakenna vastaava sovellus prompteilla

Alla olevat promptit on tarkoitettu käytettäväksi **yksi kerrallaan**
ohjelmointia osaavan tekoälyavustajan kanssa. Prompti on ohje, jossa kerrotaan
avustajalle tavoite, reunaehdot ja tapa todentaa tulos. Vaiheittaisessa
työskentelyssä jokaisen vaiheen tulos tarkistetaan ennen seuraavaa.

### Ennen aloitusta

1. Asenna Python 3, Ollama ja jokin Ollama-chat-malli.
2. Avaa tyhjä projektikansio ohjelmointieditorissa, jossa on tekoälyavustaja.
3. Lähetä alla olevat promptit järjestyksessä. Pyydä avustajaa tutkimaan
   projektin nykytila ennen tiedostojen muuttamista.
4. Aja ja kokeile sovellusta jokaisen vaiheen jälkeen. Jos jokin testi
   epäonnistuu, pyydä ensin korjausta äläkä jatka seuraavaan ominaisuuteen.
5. Vaihda promptien malli tai portti vain, jos oma ympäristösi tarvitsee sen;
   käytä samaa mallin nimeä sekä koodissa että `ollama pull` -komennossa.

### Prompti 1 – määritä tavoite ja rakenne

```text
Tutki ensin avoimen projektin tiedostot ja kerro lyhyesti, mitä siellä jo on.
Tee suunnitelma suomenkieliselle selaimessa toimivalle tekoälykyselylle.
Käyttöliittymä tulee tiedostoon index.html ja paikallinen palvelin tiedostoon
app.py. Palvelin käyttää vain Pythonin vakiokirjastoa ja välittää keskustelun
paikalliselle Ollama-palvelimelle osoitteessa http://127.0.0.1:11434.
Älä vielä kirjoita koodia. Luettele komponentit, rajapinnat, käynnistysvaiheet
ja testit. Kysy, jos suunnitelmassa on ratkaisematon valinta.
```

**Tarkista:** suunnitelmassa ovat selain, Python-välityspalvelin ja Ollama;
mikrofoni ja puheeksi luku on nimetty erillisiksi selainominaisuuksiksi.

### Prompti 2 – toteuta paikallinen Python-palvelin

```text
Toteuta hyväksytyn suunnitelman mukainen app.py. Käytä vain Pythonin
vakiokirjastoa. Tarjoa index.html osoitteessa http://localhost:8000 ja
POST-rajapinta /api/chat, joka välittää validoidun messages-keskustelulistan
Ollaman POST-rajapintaan http://127.0.0.1:11434/api/chat. Käytä mallina
jobautomation/OpenEuroLLM-Finnish:latest ja aseta Ollama-pyynnön stream-arvoksi
false. Lue pyynnöstä valinnainen model-merkkijono; käytä sen puuttuessa
oletusmallia. Tarkista, että mallin nimi on merkkijono.
Palauta vastauksen teksti JSON-muodossa. Palauta virheistä selkeä HTTP-virhe
ja suomenkielinen virheviesti; älä peitä Ollaman yhteysvirheitä.
Sido palvelin vain osoitteeseen 127.0.0.1. Lisää tarvittavat CORS-otsakkeet
paikallista käyttöä varten, mutta älä avaa palvelinta kaikille verkkoliitännöille.
Kerro, mitä tiedostoa muutit ja miten testaan rajapinnan. Älä lisää riippuvuuksia.
```

**Tarkista:** `python app.py` käynnistää palvelimen ja virhe Ollaman puuttuessa
näkyy ymmärrettävänä viestinä.

### Prompti 3 – rakenna käyttöliittymä ja tekstikeskustelu

```text
Toteuta index.html suomenkieliselle, saavutettavalle keskustelusivulle.
Käytä tavallista HTML:ää, CSS:ää ja selaimen JavaScriptiä; älä lisää kirjastoja,
CDN-linkkejä tai rakennusvaihetta. Lisää viestihistoria, kysymyskenttä,
lähetyspainike, Enter-lähetys sekä Shift+Enter-rivinvaihto.
Yhdistä käyttöliittymä POST-osoitteeseen http://127.0.0.1:8000/api/chat.
Lähetä rooleilla system, user ja assistant varustettu messages-lista sekä
Ollama-mallin nimi. Näytä odotustila ja ilmoita palvelinvirhe käyttäjälle.
Älä tulkitse mallin vastausta HTML:ksi. Lisää käyttöohjeen päivitys README.md:hen.
Toteuta vain tekstikeskustelu tässä vaiheessa ja kerro, miten sen voi testata.
```

**Tarkista:** tekstikysymys lähtee palvelimelle, vastaus lisätään keskusteluun,
useampi vuoro säilyttää historian eikä virhetilanne näytä onnistumiselta.

### Prompti 4 – lisää mikrofonilla sanelu

```text
Lisää index.html:n kysymyskenttään mikrofonipainike, joka käyttää selaimen
SpeechRecognition- tai webkitSpeechRecognition-rajapintaa. Aseta tunnistuksen
kieleksi fi-FI, pyydä käyttöoikeus selaimen normaalin mikrofonilupaprosessin
kautta ja lisää tunnistettu puhe tekstikenttään. Älä lähetä kysymystä
automaattisesti: käyttäjän pitää voida tarkistaa tai muokata tunnistettua tekstiä
ja lähettää se itse.
Näytä kuuntelutila, salli kuuntelun keskeyttäminen ja ilmoita ymmärrettävästi
luvan puuttumisesta, puheesta jota ei tunnistettu sekä selaimesta, joka ei tue
rajapintaa. Älä väitä puheentunnistusta paikalliseksi; kerro käyttöliittymässä
ja README.md:ssä, että selain voi käyttää verkkopohjaista tunnistuspalvelua.
Älä muuta palvelimen chat-rajapintaa. Testaa myös, että tekstillä kysyminen
toimii edelleen.
```

**Tarkista:** luvan antamisen jälkeen sanelu täyttää tekstikentän, mutta ei
lähetä kysymystä ennen käyttäjän toimintaa.

### Prompti 5 – lue tekoälyn vastaus puheena

```text
Lisää vastauksen ääneen lukeminen selaimen speechSynthesis- ja
SpeechSynthesisUtterance-rajapinnoilla. Aseta puheen kieleksi fi-FI ja valitse
saatavilla oleva suomenkielinen ääni, jos sellainen löytyy; älä lupaa, että ääni
on jokaisessa selaimessa saatavilla. Lisää äänen mykistys ja puheen
keskeytyspainike. Säilytä mykistysvalinta selaimen localStorage-tallennuksessa.
Puhesynteesin puuttuessa tekstivastausten pitää edelleen näkyä normaalisti.
Kerro README.md:ssä, että ääni tulee selaimesta eikä tekoälymallista.
Älä sekoita puheentunnistuksen käyttöoikeutta puhesynteesiin. Testaa sekä ääni
päällä että pois ja keskeytys puheen aikana.
```

**Tarkista:** vastaus näkyy aina tekstinä; jos selain tukee suomenkielistä
puhetta, vastaus myös kuuluu ja sen voi mykistää tai keskeyttää.

### Prompti 6 – lisää mallit, lataustila ja käyttöohje

```text
Lisää tarvittaessa GET /api/models -rajapinta, joka listaa Ollaman asennetut
mallit /api/tags-rajapinnasta, ja käyttöliittymään mallivalitsin. Tarkista
valittu malli palvelimella ennen sen käyttöä. Näytä mallin lataus ja virhe
selvästi. Päivitä README.md niin, että siinä ovat asennusvaatimukset, mallin
latauskomennot, käynnistys, selaimen puheominaisuudet ja tietosuojarajoitukset.
Pidä kaikki riippuvuudet Pythonin vakiokirjastossa ja selaimen natiiveissa
rajapinnoissa. Kerro lopuksi muuttuneet tiedostot ja täsmälliset testikomennot.
```

**Tarkista:** valitsin näyttää asennetut mallit; virheellinen tai puuttuva malli
ei aiheuta virheellistä onnistumisviestiä.

### Prompti 7 – testaa koko käyttötapaus ja korjaa havainnot

```text
Tarkista koko sovellus toteutuneita tiedostoja vasten. Suorita mahdolliset
olemassa olevat testit ja lisää pienet kohdennetut testit vain, jos projektiin
sopiva tapa on jo olemassa. Kokeile tai kuvaa todennettavasti nämä tapaukset:
1) palvelin käynnistyy ja etusivu latautuu, 2) tekstikysymys saa Ollama-vastauksen,
3) keskustelun aiemmat vuorot säilyvät, 4) mikrofonin puhe näkyy kentässä eikä
lähetä itsestään, 5) vastauksen puhe voidaan mykistää ja keskeyttää,
6) selaimen puheominaisuuksien puuttuessa tekstikäyttö toimii, 7) Ollaman yhteysvirhe näytetään
selkeästi. Korjaa havaitsemasi tämän sovelluksen toimintaan liittyvät viat.
Älä väitä testanneesi mikrofonia tai ääntä oikeassa selaimessa, jos et oikeasti
voi käyttää selainta ja mikrofonia. Raportoi testikomennot ja tulokset.
```

**Tarkista:** pyydä avustajaa erottamaan suoritetut testit niistä
selain-/mikrofonitesteistä, joita ei voitu suorittaa.

### Promptausharjoitus oppilaille

Käyttäkää samaa tehtävää ja muuttakaa yhdessä yhtä vaatimusta kerrallaan,
esimerkiksi vastausten kohderyhmää, vastausten pituutta tai käyttöliittymän
väriteemaa. Ennustakaa ennen promptia, mikä muuttuu. Tarkistakaa muutoksen
jälkeen, toteutuiko se ja rikkoutuiko jokin aiempi vaatimus. Hyvässä promptissa
on tavoite, rajaus, odotettu toiminta ja tapa testata onnistuminen. Pyytäkää
tekoälyä kertomaan, mitä se muutti ja mitä se ei pystynyt testaamaan.
