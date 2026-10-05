# Kysely

Selainpohjainen kyselysivu, joka käyttää paikallista Ollama-mallia
`jobautomation/OpenEuroLLM-Finnish:latest`. Kysely-sovellus käsittelee
keskustelun paikallisesti eikä lähetä sitä pilvipalveluun.

Kysymyksen voi kirjoittaa tai sanella mikrofonipainikkeella. Sanelu käyttää
selaimen suomenkielistä puheentunnistusta, joka voi selaimesta riippuen
käsitellä ääntä selaimen omassa pilvipalvelussa. Sanelu vaatii selaimen
mikrofoniluvan; ominaisuus toimii vain puheentunnistusta tukevissa selaimissa.

## Käynnistys

1. Asenna Ollama ja varmista, että malli löytyy koneelta:

   ```powershell
   ollama pull jobautomation/OpenEuroLLM-Finnish:latest
   ```

2. Käynnistä Ollama, jos se ei ole jo käynnissä.
3. Avaa tämä kansio terminaalissa ja käynnistä sivu:

   ```powershell
   python app.py
   ```

4. Avaa selaimessa <http://localhost:8000>.

Palvelin välittää keskustelun koneen omaan Ollama-rajapintaan osoitteessa
`http://127.0.0.1:11434`. Sivun ajamiseen ei tarvita Python-lisäpaketteja.
Kyselysivu voi olla auki myös suoraan HTML-tiedostona tai editorin esikatselussa;
API-pyynnöt ohjataan silti paikalliseen palvelimeen.
