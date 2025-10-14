document.addEventListener("DOMContentLoaded", () => {
  const apiKeyElement = document.getElementById("csc-api-key");
  if (!apiKeyElement) {
    console.error("Erro: elemento 'csc-api-key' não encontrado.");
    return;
  }

  const apiKey = JSON.parse(apiKeyElement.textContent);
  const baseUrl = "https://api.countrystatecity.in/v1";

  const countrySelect = document.getElementById("country");
  const stateSelect = document.getElementById("state");
  const citySelect = document.getElementById("city");

  fetch(`${baseUrl}/countries`, {
    headers: { "X-CSCAPI-KEY": apiKey }
  })
  .then(res => res.json())
  .then(data => {
    data.forEach(country => {
      const option = document.createElement("option");
      option.value = country.iso2;
      option.textContent = country.name;
      countrySelect.appendChild(option);
    });
  });

  countrySelect.addEventListener("change", () => {
    const countryCode = countrySelect.value;
    stateSelect.innerHTML = '<option value="">Selecione um estado</option>';
    citySelect.innerHTML = '<option value="">Selecione uma cidade</option>';

    if (!countryCode) return;

    fetch(`${baseUrl}/countries/${countryCode}/states`, {
      headers: { "X-CSCAPI-KEY": apiKey }
    })
    .then(res => res.json())
    .then(states => {
      states.forEach(state => {
        const option = document.createElement("option");
        option.value = state.iso2;
        option.textContent = state.name;
        stateSelect.appendChild(option);
      });
    });
  });

  stateSelect.addEventListener("change", () => {
    const countryCode = countrySelect.value;
    const stateCode = stateSelect.value;
    citySelect.innerHTML = '<option value="">Selecione uma cidade</option>';

    if (!countryCode || !stateCode) return;

    fetch(`${baseUrl}/countries/${countryCode}/states/${stateCode}/cities`, {
      headers: { "X-CSCAPI-KEY": apiKey }
    })
    .then(res => res.json())
    .then(cities => {
      cities.forEach(city => {
        const option = document.createElement("option");
        option.textContent = city.name;
        citySelect.appendChild(option);
      });
    });
  });
});
