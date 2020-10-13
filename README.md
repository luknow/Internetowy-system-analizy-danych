# Internetowy system analizy danych
Przejdź do systemu: https://analiza.herokuapp.com <br>
lub zobacz filmiki: https://drive.google.com/drive/folders/1M5OEleX_Alq8HhVI8e1duj1q2D9dvA-l

<h2>Opis aplikacji</h2>
System został stworzony przede wszystkim do analizy odpowiedzi uzyskanych z ankiet Google, natomiast umożliwia równiez analizę dowolnego
arkusza Excela wczytanego z dysku Google. Aby przystąpić do anlizy należy zalogowac się kontem Google i wybrać arkusz do wczytania.

<h3>Technologia</h3>
<h4>Serwer</h4>
<ul>
  <li>Flask</li>
  <li>Seaborn</li>
  <li>Google Drive REST API</li>
  <li>OAuth 2.0</li>
 </ul>
<h4>Klient</h4>
<ul>
  <li>pdfMake</li>
  <li>Bootstrap</li>
  <li>jQuery</li>
  <li>DataTables</li>
</ul>

<h3>Wymagania funkcjonalne</h3>
<ol>
  <li>dostęp do aplikacji,</li>
  <ul>
    <li>aplikacja musi umozliwić zalogowanie się kontem Google,</li>
    <li>aplikacja musi umozliwić wylogowanie się.</li>
  </ul>
  <li>pozyskanie danych,</li>
    <ul>
    <li>aplikacja musi umozliwić wczytanie arkusza kalkulacyjnego Excela
znajdującego się na dysku Google zalogowanego użytkownika.</li>
  </ul>
  <li>przygotowanie danych do analizy,</li>
  <ul>
    <li>aplikacja musi umożliwić zastąpienie pustych wartości,</li>
    <li>aplikacja musi wyświetlić obserwacje odstające (tzw. outliery) dla
wybranego atrybutu liczbowego,</li>
    <li>aplikacja musi umożliwić wyszukiwanie i zamienianie wartości dla
wybranego atrybutu.</li>
  </ul>
  <li>informacje dla poszczególnych atrybutów,</li>
  <ul>
    <li>aplikacja musi wyświetlić następujące informacje:</li>
     <ol type="a">
      <li>atrybuty typu liczbowego,</li>
        <ul style="list-style-type:square">
          <li>liczność,</li>
          <li>średnia,</li>
          <li>odchylenie standardowe,</li>
          <li>wartość minimalna,</li>
          <li>wartość maksymalna,</li> 
          <li>pierwszy kwartyl,</li>
          <li>drugi kwartyl,</li>
          <li>trzeci kwartyl.</li>
        </ul>
       <li>atrybuty typu tekstowego.</li>
        <ul style="list-style-type:square">
         <li>liczność wszystkich wartości atrybutu,</li>
         <li>liczność unikalnych wartości atrybutu,</li>
         <li>najczęściej występująca wartość,</li>
         <li>liczność dla najczęściej występującej wartości.</li>
        </ul>
     </ol> 
    <li>aplikacja musi wyświetlić wartości dla wybranego atrybutu,</li>
    <li>aplikacja musi umożliwić eksport wartości wybranego atrybutu do następujących formatów:</li>
     <ul style="list-style-type:square">
         <li>CSV,</li>
         <li>EXCEL,</li>
         <li>PDF.</li>
        </ul>
    <li>aplikacja musi wyświetlić wykresy słupkowe i pudełkowe dla wybranego atrybutu,</li>
    <li>aplikacja musi umożliwić pobranie raportu dla wybranego atrybutu zawierającego wygenerowane wykresy pudełkowy i słupkowy oraz informacje:</li>
     <ul style="list-style-type:square">
       <li>atrybut liczbowy – jak podano w pkt. 4 ppkt. (a),</li>
       <li>atrybut tekstowy – jak podano w pkt. 4 ppkt. (b).</li>
     </ul>
  </ul>
  <li>informacje dla wszystkich atrybutów,</li>
    <ul>
      <li>aplikacja musi wyświetlić korelację uwzględniając wszystkie atrybuty typu liczbowego (jeżeli arkusz posiada atrybuty typu liczbowego),</li>
      <li>aplikacja musi wyświetlić następujące informacje:</li>
        <ol type="a">
          <li>jeżeli arkusz posiada atrybuty typu liczbowego – jak podano w pkt. 4 ppkt. (a),</li>
          <li>jeżeli arkusz nie posiada atrybutów typu liczbowego to uwzględniając wszystkie atrybuty typu tekstowego – jak podano w pkt. 4 ppkt. (b).</li>
        </ol>
      <li>aplikacja musi przedstawić wartości arkusza w postaci tabeli,</li>
      <li>aplikacja musi umożliwić eksport wartości wybranego arkusza do następujących formatów:</li>
        <ul style="list-style-type:square">
         <li>CSV,</li>
         <li>EXCEL,</li>
         <li>PDF.</li>
        </ul>
      <li>aplikacja musi umożliwić pobranie raportu dla wszystkich atrybutów zawierającego informacje jak podano w pkt. 5 z uwzględnieniem warunku dla ppkt. (a) oraz ppkt. (b).</li>
    </ul>
  <li>testy statystyczne,</li>
    <ul>
      <li>aplikacja musi umożliwić przeprowadzenie następujących testów statystycznych dla wybranych przez użytkownika atrybutów (minimalnie 2, maksymalnie 5 atrybutów):</li>
        <ul style="list-style-type:square">
          <li>Chi-kwadrat,</li>
          <li>Kruskal-Wallis,</li>
          <li>U Mann-Whitney,</li>
          <li>Korelacja Rho-Spearmana.</li>
        </ul>
      <li>aplikacja po przeprowadzeniu testu musi wyświetlić następujące informacje:</li>
         <ol type="a">
           <li>Chi-kwadrat, Kruskal-Wallis, U Mann-Whitney,</li>
            <ul style="list-style-type:square">
              <li>hipotezy statystyczne,</li>
              <li>wartość testu,</li>
              <li>wartość p,</li>
              <li>decyzja.</li>
            </ul>
           <li>Korelacja Rho-Spearmana.</li>
            <ul style="list-style-type:square">
              <li>wartość testu,</li>
              <li>wartość p,</li>
              <li>decyzja.</li>
           </ul>
         </ol>
      <li>aplikacja po przeprowadzeniu testu  musi wyświetlić wykres pudełkowy,</li>
<li>aplikacja musi umożliwić pobranie raportu przeprowadzonych testów zawierającego wykres pudełkowy oraz informacje jak podano w pkt. 6 z uwzględnieniem warunku dla ppkt. (a) oraz ppkt. (b).</li>
    </ul>
  <li>zestawienie atrybutów.</li>
     <ul>
       <li>aplikacja musi umożliwić uzyskanie informacji dla wybranych przez użytkownika atrybutów (minimalnie 2, maksymalnie 5 atrybutów),</li>
       <li>aplikacja musi wyświetlić informacje jak podano w pkt. 4 ppkt. (a),</li>
       <li>jeżeli wśród wybranych przez użytkownika atrybutów znajduje się co najmniej jeden atrybut typu liczbowego to aplikacja musi wyświetlić korelację,</li>
       <li>aplikacja musi wyświetlić wartości wybranych atrybutów w postaci tabeli,</li>
       <li>aplikacja musi umożliwić eksport wartości wybranych atrybutów do następujących formatów:</li>
        <ul style="list-style-type:square">
         <li>CSV,</li>
         <li>EXCEL,</li>
         <li>PDF.</li>
         </ul>
       <li>aplikacja musi umożliwić pobranie raportu zawierającego informacje jak podano w pkt. 4 ppkt. (a). Jeżeli wśród wybranych przez użytkownika atrybutów znajduje się co najmniej jeden atrybut typu liczbowego to raport dodatkowo musi zawierać korelację.</li>
     </ul>
</ol>
