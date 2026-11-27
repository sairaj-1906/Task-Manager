const taskCheckboxes = Array.from(
  document.querySelectorAll("[data-task-select]"),
);
const selectAllCheckboxes = Array.from(
  document.querySelectorAll("[data-select-all]"),
);
const selectedCount = document.querySelector("[data-selected-count]");

const updateTaskSelection = () => {
  const selectedIds = new Set(
    taskCheckboxes
      .filter((checkbox) => checkbox.checked)
      .map((checkbox) => checkbox.dataset.taskId),
  );
  taskCheckboxes.forEach((checkbox) => {
    checkbox.checked = selectedIds.has(checkbox.dataset.taskId);
  });
  selectAllCheckboxes.forEach((checkbox) => {
    checkbox.checked =
      selectedIds.size > 0 &&
      new Set(taskCheckboxes.map((item) => item.dataset.taskId)).size ===
        selectedIds.size;
    checkbox.indeterminate =
      selectedIds.size > 0 && !checkbox.checked;
  });
  if (selectedCount) {
    selectedCount.textContent = String(selectedIds.size);
  }
};

taskCheckboxes.forEach((checkbox) => {
  checkbox.addEventListener("change", updateTaskSelection);
});

selectAllCheckboxes.forEach((checkbox) => {
  checkbox.addEventListener("change", () => {
    taskCheckboxes.forEach((taskCheckbox) => {
      taskCheckbox.checked = checkbox.checked;
    });
    updateTaskSelection();
  });
});
