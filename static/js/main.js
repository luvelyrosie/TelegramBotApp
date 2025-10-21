window.socket = null;

document.addEventListener("DOMContentLoaded", () => {
    const path = window.location.pathname;
    const onTaskListPage = path.match(/\/tasks\/tasklist\/(\d+)\//);
    const taskListContainer = document.getElementById("task-list");

    if (!onTaskListPage || !taskListContainer) return;

    const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${wsProtocol}://${window.location.host}/ws/tasks/`;
    window.socket = new WebSocket(wsUrl);

    window.socket.onopen = () => console.log("WebSocket connected");
    window.socket.onclose = e => console.log("WebSocket disconnected:", e.reason || "");
    window.socket.onerror = err => console.error("WebSocket error:", err);

    function showToast(message) {
        const toast = document.createElement("div");
        toast.className = "alert alert-info position-fixed top-0 end-0 m-3 shadow";
        toast.style.zIndex = "1055";
        toast.innerHTML = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

    function updateTaskCard(task) {
        const card = document.getElementById(`task-${task.id}`);
        if (card) {
            card.querySelector(".card-title").textContent = task.title;
            const status = card.querySelector(".text-success, .text-warning");
            if (status) {
                status.className = task.is_done ? "text-success" : "text-warning";
                status.textContent = task.is_done ? "Done" : "Pending";
            }
        } else {
            const newCard = document.createElement("div");
            newCard.className = "col-md-6";
            newCard.id = `task-${task.id}`;
            newCard.innerHTML = `
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title">${task.title}</h5>
                        <p class="mb-1"><strong>Status:</strong> 
                            <span class="${task.is_done ? 'text-success' : 'text-warning'}">
                                ${task.is_done ? 'Done' : 'Pending'}
                            </span>
                        </p>
                    </div>
                </div>
            `;
            taskListContainer.prepend(newCard);
        }
    }

    window.socket.onmessage = event => {
        try {
            const task = JSON.parse(event.data);
            console.log("Task update received:", task);

            updateTaskCard(task);

            if (task.hasOwnProperty("created")) {
                let message = "";
                if (task.created) {
                    message = `<strong>${task.title}</strong> was created!`;
                } else if (task.is_done) {
                    message = `<strong>${task.title}</strong> was marked as done!`;
                } else {
                    message = `<strong>${task.title}</strong> was updated!`;
                }
                showToast(message);
            }

        } catch (e) {
            console.error("Error parsing WebSocket message:", e, event.data);
        }
    };
});