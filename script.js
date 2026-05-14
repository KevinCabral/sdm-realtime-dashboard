const editalRows = [
  {
    concelho: "Praia",
    zona: "Paiol",
    mesa: "PR-AO-01",
    inscritos: 440,
    mpd: 101,
    paicv: 99,
    ucid: 23,
    pts: 6,
    pp: 9,
    brancos: 9,
    nulos: 3,
    boletinsIniciais: 480,
    boletinsInutilizados: 6,
  },
  {
    concelho: "Praia",
    zona: "Paiol",
    mesa: "PR-AO-02",
    inscritos: 400,
    mpd: 80,
    paicv: 120,
    ucid: 20,
    pts: 4,
    pp: 5,
    brancos: 7,
    nulos: 4,
    boletinsIniciais: 440,
    boletinsInutilizados: 3,
  },
  {
    concelho: "Praia",
    zona: "Várzea",
    mesa: "PR-VZ-01",
    inscritos: 500,
    mpd: 130,
    paicv: 140,
    ucid: 30,
    pts: 10,
    pp: 8,
    brancos: 6,
    nulos: 5,
    boletinsIniciais: 540,
    boletinsInutilizados: 2,
  },
  {
    concelho: "Mindelo",
    zona: "Ribeira Bote",
    mesa: "MD-RB-01",
    inscritos: 460,
    mpd: 115,
    paicv: 110,
    ucid: 25,
    pts: 5,
    pp: 7,
    brancos: 8,
    nulos: 4,
    boletinsIniciais: 500,
    boletinsInutilizados: 4,
  },
];

const concelhoFilter = document.getElementById("concelhoFilter");
const zonaFilter = document.getElementById("zonaFilter");
const mesaFilter = document.getElementById("mesaFilter");
const tableBody = document.querySelector("#resultsTable tbody");
const totalsRow = document.getElementById("totalsRow");

function withComputedFields(row) {
  const votantes = row.mpd + row.paicv + row.ucid + row.pts + row.pp + row.brancos + row.nulos;
  const boletinsUtilizados = votantes + row.boletinsInutilizados;
  const boletinsRestantes = row.boletinsIniciais - boletinsUtilizados;

  return {
    ...row,
    votantes,
    boletinsUtilizados,
    boletinsRestantes,
  };
}

function uniqueValues(rows, key) {
  return [...new Set(rows.map((item) => item[key]))].sort((a, b) => a.localeCompare(b));
}

function fillSelect(selectElement, values, selectedValue = "Todos") {
  const previous = values.includes(selectElement.value) ? selectElement.value : selectedValue;
  selectElement.innerHTML = "";

  const allOption = document.createElement("option");
  allOption.value = "Todos";
  allOption.textContent = "Todos";
  selectElement.appendChild(allOption);

  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    selectElement.appendChild(option);
  });

  selectElement.value = previous;
}

function filteredRows() {
  return editalRows
    .filter((row) => concelhoFilter.value === "Todos" || row.concelho === concelhoFilter.value)
    .filter((row) => zonaFilter.value === "Todos" || row.zona === zonaFilter.value)
    .filter((row) => mesaFilter.value === "Todos" || row.mesa === mesaFilter.value)
    .map(withComputedFields);
}

function updateFilterOptions() {
  fillSelect(concelhoFilter, uniqueValues(editalRows, "concelho"));

  const zonaSource =
    concelhoFilter.value === "Todos"
      ? editalRows
      : editalRows.filter((row) => row.concelho === concelhoFilter.value);
  fillSelect(zonaFilter, uniqueValues(zonaSource, "zona"));

  const mesaSource = editalRows
    .filter((row) => concelhoFilter.value === "Todos" || row.concelho === concelhoFilter.value)
    .filter((row) => zonaFilter.value === "Todos" || row.zona === zonaFilter.value);
  fillSelect(mesaFilter, uniqueValues(mesaSource, "mesa"));
}

function renderRows() {
  const rows = filteredRows();
  tableBody.innerHTML = "";

  rows.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.concelho}</td>
      <td>${row.zona}</td>
      <td>${row.mesa}</td>
      <td>${row.inscritos}</td>
      <td class="col-votantes">${row.votantes}</td>
      <td>${row.mpd}</td>
      <td>${row.paicv}</td>
      <td>${row.ucid}</td>
      <td>${row.pts}</td>
      <td>${row.pp}</td>
      <td>${row.brancos}</td>
      <td>${row.nulos}</td>
      <td class="col-iniciais">${row.boletinsIniciais}</td>
      <td>${row.boletinsInutilizados}</td>
      <td class="col-restantes">${row.boletinsRestantes}</td>
      <td class="col-utilizados">${row.boletinsUtilizados}</td>
    `;
    tableBody.appendChild(tr);
  });
}

function renderTotals() {
  const rows = filteredRows();
  const totals = rows.reduce(
    (acc, row) => {
      acc.inscritos += row.inscritos;
      acc.votantes += row.votantes;
      acc.mpd += row.mpd;
      acc.paicv += row.paicv;
      acc.ucid += row.ucid;
      acc.pts += row.pts;
      acc.pp += row.pp;
      acc.brancos += row.brancos;
      acc.nulos += row.nulos;
      acc.boletinsIniciais += row.boletinsIniciais;
      acc.boletinsInutilizados += row.boletinsInutilizados;
      acc.boletinsRestantes += row.boletinsRestantes;
      acc.boletinsUtilizados += row.boletinsUtilizados;
      return acc;
    },
    {
      inscritos: 0,
      votantes: 0,
      mpd: 0,
      paicv: 0,
      ucid: 0,
      pts: 0,
      pp: 0,
      brancos: 0,
      nulos: 0,
      boletinsIniciais: 0,
      boletinsInutilizados: 0,
      boletinsRestantes: 0,
      boletinsUtilizados: 0,
    }
  );

  totalsRow.innerHTML = `
    <td colspan="3">Totais</td>
    <td>${totals.inscritos}</td>
    <td class="col-votantes">${totals.votantes}</td>
    <td>${totals.mpd}</td>
    <td>${totals.paicv}</td>
    <td>${totals.ucid}</td>
    <td>${totals.pts}</td>
    <td>${totals.pp}</td>
    <td>${totals.brancos}</td>
    <td>${totals.nulos}</td>
    <td class="col-iniciais">${totals.boletinsIniciais}</td>
    <td>${totals.boletinsInutilizados}</td>
    <td class="col-restantes">${totals.boletinsRestantes}</td>
    <td class="col-utilizados">${totals.boletinsUtilizados}</td>
  `;
}

function render() {
  updateFilterOptions();
  renderRows();
  renderTotals();
}

[concelhoFilter, zonaFilter, mesaFilter].forEach((select) => {
  select.addEventListener("change", render);
});

render();
