(function () {
  const rowsContainer = document.getElementById("item-rows");
  if (!rowsContainer) {
    return;
  }

  const totalFormsInput = document.getElementById("id_form-TOTAL_FORMS");
  const topDropZone = document.getElementById("item-rows-drop-zone");
  const existingItemIds = new Set(
    (rowsContainer.dataset.existingItems || "")
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean)
  );

  let draggingRow = null;
  let dragSlot = null;
  let dropIndicator = null;
  let dragOffsetX = 0;
  let dragOffsetY = 0;

  function getRows() {
    return Array.from(rowsContainer.querySelectorAll(".item-row"));
  }

  function reindexRows() {
    getRows().forEach((row, index) => {
      row.querySelectorAll("[name]").forEach((element) => {
        element.name = element.name.replace(/form-\d+-/, `form-${index}-`);
      });
      row.querySelectorAll("[id]").forEach((element) => {
        element.id = element.id.replace(/id_form-\d+-/, `id_form-${index}-`);
      });
    });

    if (totalFormsInput) {
      totalFormsInput.value = String(getRows().length);
    }
  }

  function getSelectedIds(excludeSelect) {
    return getRows()
      .map((row) => row.querySelector('select[name$="-item"]'))
      .filter((select) => select && select !== excludeSelect && select.value)
      .map((select) => select.value);
  }

  function syncProductOptions() {
    getRows().forEach((row) => {
      const select = row.querySelector('select[name$="-item"]');
      if (!select) {
        return;
      }

      const blockedIds = new Set([
        ...getSelectedIds(select),
        ...existingItemIds,
      ]);

      Array.from(select.options).forEach((option) => {
        if (!option.value) {
          option.disabled = false;
          return;
        }
        option.disabled =
          blockedIds.has(option.value) && option.value !== select.value;
      });
    });
  }

  function removeDropIndicator() {
    if (dropIndicator) {
      dropIndicator.remove();
      dropIndicator = null;
    }
    if (topDropZone) {
      topDropZone.classList.remove("is-active");
    }
  }

  function findInsertPosition(clientY) {
    const rows = getRows().filter((row) => row !== draggingRow);

    if (topDropZone) {
      const zoneRect = topDropZone.getBoundingClientRect();
      if (clientY <= zoneRect.bottom) {
        return { row: rows[0] || null, before: true, useTopZone: true };
      }
    }

    for (const row of rows) {
      const rect = row.getBoundingClientRect();
      if (clientY < rect.top + rect.height / 2) {
        return { row, before: true, useTopZone: false };
      }
    }

    const lastRow = rows[rows.length - 1];
    return { row: lastRow || null, before: false, useTopZone: false };
  }

  function showDropIndicator(clientY) {
    removeDropIndicator();
    const position = findInsertPosition(clientY);

    if (position.useTopZone && topDropZone) {
      topDropZone.classList.add("is-active");
      return;
    }

    if (!position.row) {
      return;
    }

    dropIndicator = document.createElement("div");
    dropIndicator.className = "item-drop-indicator";

    if (position.before) {
      position.row.before(dropIndicator);
    } else {
      position.row.after(dropIndicator);
    }
  }

  function applyInsertPosition(clientY) {
    const position = findInsertPosition(clientY);

    if (!draggingRow) {
      return;
    }

    if (position.useTopZone) {
      if (position.row) {
        rowsContainer.insertBefore(draggingRow, position.row);
      } else if (topDropZone) {
        topDropZone.after(draggingRow);
      } else {
        rowsContainer.prepend(draggingRow);
      }
      return;
    }

    if (position.row) {
      if (position.before) {
        position.row.before(draggingRow);
      } else {
        position.row.after(draggingRow);
      }
      return;
    }

    rowsContainer.appendChild(draggingRow);
  }

  function endDrag(clientY) {
    if (!draggingRow) {
      return;
    }

    applyInsertPosition(clientY);

    draggingRow.classList.remove("is-dragging");
    draggingRow.style.position = "";
    draggingRow.style.left = "";
    draggingRow.style.top = "";
    draggingRow.style.width = "";
    draggingRow.style.zIndex = "";
    draggingRow.style.pointerEvents = "";

    if (dragSlot) {
      dragSlot.remove();
      dragSlot = null;
    }

    removeDropIndicator();
    rowsContainer.classList.remove("is-dragging");
    draggingRow = null;

    document.removeEventListener("mousemove", onMouseMove);
    document.removeEventListener("mouseup", onMouseUp);

    reindexRows();
    syncProductOptions();
  }

  function onMouseMove(event) {
    if (!draggingRow) {
      return;
    }

    draggingRow.style.left = `${event.clientX - dragOffsetX}px`;
    draggingRow.style.top = `${event.clientY - dragOffsetY}px`;
    showDropIndicator(event.clientY);
  }

  function onMouseUp(event) {
    endDrag(event.clientY);
  }

  function startDrag(row, event) {
    if (draggingRow) {
      return;
    }

    draggingRow = row;
    const rect = row.getBoundingClientRect();

    dragSlot = document.createElement("div");
    dragSlot.className = "item-row-slot";
    dragSlot.style.height = `${rect.height}px`;
    rowsContainer.insertBefore(dragSlot, row);

    dragOffsetX = event.clientX - rect.left;
    dragOffsetY = event.clientY - rect.top;

    row.classList.add("is-dragging");
    row.style.position = "fixed";
    row.style.left = `${rect.left}px`;
    row.style.top = `${rect.top}px`;
    row.style.width = `${rect.width}px`;
    row.style.zIndex = "1000";
    row.style.pointerEvents = "none";

    rowsContainer.classList.add("is-dragging");

    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
  }

  function cloneRow() {
    const rows = getRows();
    const sourceRow = rows[rows.length - 1];
    const newRow = sourceRow.cloneNode(true);

    newRow.querySelectorAll(".text-danger").forEach((element) => element.remove());

    const itemSelect = newRow.querySelector('select[name$="-item"]');
    if (itemSelect) {
      itemSelect.selectedIndex = 0;
    }

    const quantityInput = newRow.querySelector('input[name$="-quantidade"]');
    if (quantityInput) {
      quantityInput.value = "1";
    }

    rowsContainer.appendChild(newRow);
    reindexRows();
    bindRowEvents(newRow);
    syncProductOptions();
  }

  function clearRow(row) {
    const itemSelect = row.querySelector('select[name$="-item"]');
    if (itemSelect) {
      itemSelect.selectedIndex = 0;
    }

    const quantityInput = row.querySelector('input[name$="-quantidade"]');
    if (quantityInput) {
      quantityInput.value = "1";
    }

    row.querySelectorAll(".text-danger").forEach((element) => element.remove());
    syncProductOptions();
  }

  function removeRow(row) {
    const rows = getRows();
    if (rows.length === 1) {
      clearRow(row);
      return;
    }

    row.remove();
    reindexRows();
    syncProductOptions();
  }

  function maybeAppendRow(changedRow) {
    syncProductOptions();

    const rows = getRows();
    const lastRow = rows[rows.length - 1];
    const itemSelect = changedRow.querySelector('select[name$="-item"]');

    if (!itemSelect || !itemSelect.value || changedRow !== lastRow) {
      return;
    }

    cloneRow();
  }

  function bindRowEvents(row) {
    const itemSelect = row.querySelector('select[name$="-item"]');
    const removeButton = row.querySelector(".btn-remove-row");
    const dragHandle = row.querySelector(".drag-handle");

    if (itemSelect) {
      itemSelect.addEventListener("change", () => maybeAppendRow(row));
    }

    if (removeButton) {
      removeButton.addEventListener("click", () => removeRow(row));
    }

    if (dragHandle) {
      dragHandle.addEventListener("mousedown", (event) => {
        if (event.button !== 0) {
          return;
        }
        event.preventDefault();
        startDrag(row, event);
      });
    }
  }

  getRows().forEach(bindRowEvents);
  syncProductOptions();

  const addRowButton = document.getElementById("item-row-add-btn");
  if (addRowButton) {
    addRowButton.addEventListener("click", () => cloneRow());
  }
})();
