// Global variables for pagination
let currentPage = 0;
let lastSearchTerm = "";

document.addEventListener("DOMContentLoaded", function () {
  initializeSliders();
  initializeGamesList();

  // Setup Load More button
  document
    .getElementById("load-more-btn")
    .addEventListener("click", function () {
      fetchGamesWithFilters(currentPage + 1).then(displayGames);
    });

  document
    .getElementById("applyFilters")
    .addEventListener("click", function () {
      document.getElementById("games-list").innerHTML = "";

      fetchGamesWithFilters()
        .then(displayGames)
        .catch((error) => {
          console.error("Failed to fetch filtered games data:", error);
        });
    });

  document
    .getElementById("searchButton")
    .addEventListener("click", function () {
      document.getElementById("games-list").innerHTML = "";

      fetchGamesWithFilters()
        .then(displayGames)
        .catch((error) => {
          console.error("Failed to search games data:", error);
        });
    });

  document
    .getElementById("gameSearch")
    .addEventListener("keypress", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        document.getElementById("games-list").innerHTML = "";

        fetchGamesWithFilters()
          .then(displayGames)
          .catch((error) => {
            console.error("Failed to search games data:", error);
          });
      }
    });
});
window.addEventListener("resize", updateDescriptions);

function initializeSliders() {
  const sliders = [
    {
      id: "difficultyRange",
      minId: "difficultyMin",
      maxId: "difficultyMax",
    },
    {
      id: "preparationRange",
      minId: "preparationMin",
      maxId: "preparationMax",
    },
    { id: "physicalRange", minId: "physicalMin", maxId: "physicalMax" },
    { id: "durationRange", minId: "durationMin", maxId: "durationMax" },
    {
      id: "groupSizeRange",
      minId: "groupSizeMin",
      maxId: "groupSizeMax",
    },
  ];

  sliders.forEach((slider) => {
    const element = document.getElementById(slider.id);
    if (element) {
      noUiSlider.create(element, {
        start: [1, 10],
        connect: true,
        step: 1,
        range: {
          min: 1,
          max: 10,
        },
      });

      const minElement = document.getElementById(slider.minId);
      const maxElement = document.getElementById(slider.maxId);

      element.noUiSlider.on("update", function (values, handle) {
        const value = Math.round(values[handle]);
        if (handle === 0) {
          minElement.innerText = value;
        } else {
          maxElement.innerText = value;
        }
      });
    }
  });
}

function initializeGamesList() {
  fetchGamesWithFilters()
    .then(displayGames)
    .catch((error) => {
      console.error("Failed to fetch games data:", error);
    });
}

function getSelectedValues(className) {
  const checkboxes = document.querySelectorAll(className + ":checked");
  return Array.from(checkboxes).map((checkbox) => checkbox.value);
}

function fetchGamesWithFilters(page = 0) {
  const tagFilters = getSelectedValues(".tag-filter");
  const ageGroupFilters = getSelectedValues(".age-filter");

  const difficultyValues = document
    .getElementById("difficultyRange")
    .noUiSlider.get();
  const preparationValues = document
    .getElementById("preparationRange")
    .noUiSlider.get();
  const physicalValues = document
    .getElementById("physicalRange")
    .noUiSlider.get();
  const durationValues = document
    .getElementById("durationRange")
    .noUiSlider.get();
  const groupSizeValues = document
    .getElementById("groupSizeRange")
    .noUiSlider.get();

  const searchTerm = document.getElementById("gameSearch").value;
  const sortBy = document.getElementById("sortBySelect").value;

  currentPage = page;

  const itemsPerPage = 20;
  const startIndex = page * itemsPerPage;

  let params = new URLSearchParams();

  if (tagFilters.length > 0) {
    tagFilters.forEach((tag) => params.append("tag_filter", tag));
  }

  if (ageGroupFilters.length > 0) {
    ageGroupFilters.forEach((age) => params.append("age_group_filter", age));
  }

  params.append("min_difficulty_index", Math.round(difficultyValues[0]));
  params.append("max_difficulty_index", Math.round(difficultyValues[1]));

  params.append("min_preperation_index", Math.round(preparationValues[0]));
  params.append("max_preperation_index", Math.round(preparationValues[1]));

  params.append("min_physical_index", Math.round(physicalValues[0]));
  params.append("max_physical_index", Math.round(physicalValues[1]));

  params.append("min_duration_index", Math.round(durationValues[0]));
  params.append("max_duration_index", Math.round(durationValues[1]));

  params.append("min_group_size_index", Math.round(groupSizeValues[0]));
  params.append("max_group_size_index", Math.round(groupSizeValues[1]));

  if (searchTerm) {
    params.append("q", searchTerm);
    lastSearchTerm = searchTerm;
  }

  params.append("sort_by", sortBy);
  params.append("start_index", startIndex);
  params.append("amount", itemsPerPage);

  return fetch(`/wiki/api/v1/games?${params.toString()}`).then((response) => {
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    return response.json();
  });
}

function displayGames(data) {
  const gamesList = document.getElementById("games-list");
  gamesList.innerHTML = ""; // Clear existing content

  if (!data.games || data.games.length === 0) {
    gamesList.innerHTML =
      '<div class="alert alert-info">No games match your filters</div>';

    // Hide pagination if no results
    document.getElementById("pagination-container").style.display = "none";
    document.getElementById("load-more-btn").style.display = "none";
    return;
  }

  // Store games data in window for other functions
  window.gamesData = data.games;

  // Update pagination info
  updatePaginationInfo(data.pagination);

  // Display games
  data.games.forEach(function (game, index) {
    const gameItem = createGameItem(game, index);
    gamesList.innerHTML += gameItem;
  });

  // Create radar charts
  data.games.forEach(function (game, index) {
    createRadarChart(game, index);
  });
}

function updateDescriptions() {
  if (!window.gamesData) return;

  const gamesList = document.getElementById("games-list");
  gamesList.innerHTML = "";

  window.gamesData.forEach(function (game, index) {
    const gameItem = createGameItem(game, index);
    gamesList.innerHTML += gameItem;
  });

  window.gamesData.forEach(function (game, index) {
    createRadarChart(game, index);
  });
}

function updatePaginationInfo(pagination) {
  const totalCount = pagination.total_count;
  const totalPages = pagination.total_pages;
  const currentPageNum = currentPage + 1; // Convert to 1-based for display

  // Show or hide load more button
  const loadMoreBtn = document.getElementById("load-more-btn");
  if (currentPageNum >= totalPages) {
    loadMoreBtn.style.display = "none";
  } else {
    loadMoreBtn.style.display = "inline-block";
  }

  // Update pagination controls
  generatePaginationControls(currentPageNum, totalPages);

  // Update the pagination count text
  const paginationInfo = document.getElementById("pagination-info");
  const startItem = currentPage * 20 + 1;
  const endItem = Math.min(currentPage * 20 + 20, totalCount);
  paginationInfo.textContent = `Showing ${startItem}-${endItem} of ${totalCount} games`;
}

function generatePaginationControls(currentPageNum, totalPages) {
  const paginationElement = document.getElementById("pagination-controls");
  paginationElement.innerHTML = "";

  // Don't show pagination for 1 page
  if (totalPages <= 1) {
    document.getElementById("pagination-container").style.display = "none";
    return;
  }

  document.getElementById("pagination-container").style.display = "flex";

  // Build pagination components
  addPreviousButton(paginationElement, currentPageNum);
  addPageNumbers(paginationElement, currentPageNum, totalPages);
  addNextButton(paginationElement, currentPageNum, totalPages);
}

function addPreviousButton(paginationElement, currentPageNum) {
  const prevLi = document.createElement("li");
  prevLi.className = `page-item ${currentPageNum === 1 ? "disabled" : ""}`;
  const prevA = document.createElement("a");
  prevA.className = "page-link";
  prevA.href = "#";
  prevA.innerHTML = "&laquo;";
  prevA.setAttribute("aria-label", "Previous");
  if (currentPageNum > 1) {
    prevA.onclick = function (e) {
      e.preventDefault();
      fetchGamesWithFilters(currentPage - 1).then(displayGames);
    };
  }
  prevLi.appendChild(prevA);
  paginationElement.appendChild(prevLi);
}

function addPageNumbers(paginationElement, currentPageNum, totalPages) {
  const maxPagesToShow = 5;
  const { startPage, endPage } = calculatePageRange(
    currentPageNum,
    totalPages,
    maxPagesToShow,
  );

  // Add first page and ellipsis if necessary
  addFirstPageIfNeeded(paginationElement, startPage);

  // Add page numbers in the range
  for (let i = startPage; i <= endPage; i++) {
    addPageNumber(paginationElement, i, currentPageNum);
  }

  // Add ellipsis and last page if necessary
  addLastPageIfNeeded(paginationElement, endPage, totalPages);
}

function calculatePageRange(currentPageNum, totalPages, maxPagesToShow) {
  let startPage = Math.max(1, currentPageNum - Math.floor(maxPagesToShow / 2));
  let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);

  // Adjust if we're near the end
  if (endPage - startPage + 1 < maxPagesToShow && startPage > 1) {
    startPage = Math.max(1, endPage - maxPagesToShow + 1);
  }

  return { startPage, endPage };
}

function addFirstPageIfNeeded(paginationElement, startPage) {
  if (startPage > 1) {
    const firstLi = document.createElement("li");
    firstLi.className = "page-item";
    const firstA = document.createElement("a");
    firstA.className = "page-link";
    firstA.href = "#";
    firstA.textContent = "1";
    firstA.onclick = function (e) {
      e.preventDefault();
      fetchGamesWithFilters(0).then(displayGames);
    };
    firstLi.appendChild(firstA);
    paginationElement.appendChild(firstLi);

    // Add ellipsis if needed
    if (startPage > 2) {
      addEllipsis(paginationElement);
    }
  }
}

function addPageNumber(paginationElement, pageNumber, currentPageNum) {
  const pageLi = document.createElement("li");
  pageLi.className = `page-item ${pageNumber === currentPageNum ? "active" : ""}`;
  const pageA = document.createElement("a");
  pageA.className = "page-link";
  pageA.href = "#";
  pageA.textContent = pageNumber;

  if (pageNumber !== currentPageNum) {
    pageA.onclick = function (e) {
      e.preventDefault();
      fetchGamesWithFilters(pageNumber - 1).then(displayGames);
    };
  }

  pageLi.appendChild(pageA);
  paginationElement.appendChild(pageLi);
}

function addLastPageIfNeeded(paginationElement, endPage, totalPages) {
  if (endPage < totalPages) {
    if (endPage < totalPages - 1) {
      addEllipsis(paginationElement);
    }

    const lastLi = document.createElement("li");
    lastLi.className = "page-item";
    const lastA = document.createElement("a");
    lastA.className = "page-link";
    lastA.href = "#";
    lastA.textContent = totalPages;
    lastA.onclick = function (e) {
      e.preventDefault();
      fetchGamesWithFilters(totalPages - 1).then(displayGames);
    };
    lastLi.appendChild(lastA);
    paginationElement.appendChild(lastLi);
  }
}

function addEllipsis(paginationElement) {
  const ellipsisLi = document.createElement("li");
  ellipsisLi.className = "page-item disabled";
  const ellipsisA = document.createElement("a");
  ellipsisA.className = "page-link";
  ellipsisA.innerHTML = "&hellip;";
  ellipsisLi.appendChild(ellipsisA);
  paginationElement.appendChild(ellipsisLi);
}

function addNextButton(paginationElement, currentPageNum, totalPages) {
  const nextLi = document.createElement("li");
  nextLi.className = `page-item ${currentPageNum === totalPages ? "disabled" : ""}`;
  const nextA = document.createElement("a");
  nextA.className = "page-link";
  nextA.href = "#";
  nextA.innerHTML = "&raquo;";
  nextA.setAttribute("aria-label", "Next");
  if (currentPageNum < totalPages) {
    nextA.onclick = function (e) {
      e.preventDefault();
      fetchGamesWithFilters(currentPage + 1).then(displayGames);
    };
  }
  nextLi.appendChild(nextA);
  paginationElement.appendChild(nextLi);
}

function generateTagsBadges(tags) {
  return tags
    .map((tag) => `<span class="badge bg-primary me-1">${tag}</span>`)
    .join("");
}

function generateAgeGroupBadges(ageGroups) {
  return ageGroups
    .map((age) => `<span class="badge bg-info me-1">${age}</span>`)
    .join("");
}

function createGameItem(game, index) {
  const shortDesc = truncateDescription(game.short_description);

  const positivePercentage = calculatePositivePercentage(
    game.upvote_count,
    game.downvote_count,
  );
  const badgeClass = getVoteBadgeClass(positivePercentage);
  const positivePercentageDisplay = isNaN(positivePercentage)
    ? "No Votes"
    : `${positivePercentage}% Positive`;

  const tagsHtml = generateTagsBadges(game.tags);
  const ageGroupsHtml = generateAgeGroupBadges(game.age_groups);

  // Add a title attribute to show users it's clickable
  const titleAttr = `Click to view details for ${game.title}`;

  return `
    <li class="list-group-item list-group-item-action" title="${titleAttr}" onclick="window.location.href='/wiki/game/${game.slug}/'" style="cursor: pointer;">
        <div class="row">
            <div class="col-xl-8 col-lg-6 order-md-1 order-1">
                <h5 class="fw-bold mb-3">${game.title}</h5>
                <div class="mb-2">
                    ${tagsHtml}
                    ${ageGroupsHtml}
                </div>
                <p>${shortDesc}</p>

            </div>

            <div class="col-xl-4 col-lg-6 order-2 mb-3 mb-md-0">
                <canvas id="radar-chart-${index}" width="150" height="125"></canvas>
            </div>

            <div class="col-xl-8 col-lg-6 order-3 mt-2 mt-md-0">
                <div class="vote-ratio">
                    <small class="text-muted">
                        <i class="fas fa-arrow-up"></i> ${game.upvote_count}
                        <i class="fas fa-arrow-down"></i> ${game.downvote_count}
                        <span class="badge ${badgeClass} ms-1">
                            ${positivePercentageDisplay}
                        </span>
                    </small>
                </div>
            </div>
        </div>
    </li>
      `;
}

function createRadarChart(game, index) {
  const ctx = document.getElementById(`radar-chart-${index}`).getContext("2d");

  new Chart(ctx, {
    type: "radar",
    data: {
      labels: [
        "Difficulty",
        "Preperation",
        "Physical",
        "Duration",
        "Group Size",
      ],
      datasets: [
        {
          label: "Game Metrics",
          data: [
            game.difficulty_index,
            game.preperation_index,
            game.physical_index,
            game.duration_index,
            game.group_size_index,
          ],
          fill: true,
          backgroundColor: "rgba(54, 162, 235, 0.2)",
          borderColor: "rgb(54, 162, 235)",
          pointBackgroundColor: "rgb(54, 162, 235)",
          pointBorderColor: "#fff",
          pointHoverBackgroundColor: "#fff",
          pointHoverBorderColor: "rgb(54, 162, 235)",
        },
      ],
    },
    options: {
      elements: {
        line: {
          borderWidth: 1,
        },
      },
      scales: {
        r: {
          angleLines: {
            display: true,
          },
          suggestedMin: 0,
          suggestedMax: 10,
          ticks: {
            display: false,
            stepSize: 2,
          },
        },
      },
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          enabled: true,
        },
      },
      maintainAspectRatio: false,
    },
  });
}

function truncateDescription(description) {
  const viewportWidth = window.innerWidth;
  let maxLength;

  if (viewportWidth <= 576) {
    maxLength = 80;
  } else if (viewportWidth <= 768) {
    maxLength = 80;
  } else if (viewportWidth <= 992) {
    maxLength = 130;
  } else if (viewportWidth <= 1200) {
    maxLength = 140;
  } else {
    maxLength = 190;
  }

  return description.length > maxLength
    ? description.substring(0, maxLength - 3) + "..."
    : description;
}

function calculatePositivePercentage(upvotes, downvotes) {
  return Math.round((upvotes / (upvotes + downvotes)) * 100);
}

function getVoteBadgeClass(percentage) {
  if (percentage > 75) {
    return "bg-success";
  } else if (percentage > 50) {
    return "bg-warning";
  } else if (percentage <= 50) {
    return "bg-danger";
  } else {
    return "bg-secondary";
  }
}
