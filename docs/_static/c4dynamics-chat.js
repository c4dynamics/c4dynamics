document.addEventListener("DOMContentLoaded", () => {
    const ENDPOINT =
        "https://f2593d8b-bdf2-4eaa-b996-45e4292e2c8d.search.ai.cloudflare.com/chat/completions";

    // ---------- Button ----------
    const button = document.createElement("button");
    button.id = "c4d-chat-button";
    button.textContent = "💬 Ask c4dynamics";
    document.body.appendChild(button);

    // ---------- Chat window ----------
    const widget = document.createElement("div");
    widget.id = "c4d-chat-widget";

    widget.innerHTML = `
        <div class="c4d-chat-header">
            <span>Ask c4dynamics</span>
            <button id="c4d-chat-close">×</button>
        </div>

        <div id="c4d-chat-messages">
            <div class="c4d-message c4d-assistant">
                Hi! Ask me anything about c4dynamics.
            </div>
        </div>

        <div class="c4d-chat-input">
            <input
                id="c4d-chat-input"
                type="text"
                placeholder="Ask about c4dynamics..."
                autocomplete="off"
            />
            <button id="c4d-chat-send">➤</button>
        </div>
    `;

    document.body.appendChild(widget);

    const messages = document.getElementById("c4d-chat-messages");
    const input = document.getElementById("c4d-chat-input");
    const send = document.getElementById("c4d-chat-send");
    const close = document.getElementById("c4d-chat-close");

    // ---------- Open / close ----------
    button.addEventListener("click", () => {
        widget.classList.add("open");
        input.focus();
    });

    close.addEventListener("click", () => {
        widget.classList.remove("open");
    });

    // ---------- Add message ----------
    function addMessage(text, type) {
        const div = document.createElement("div");
        div.className = `c4d-message c4d-${type}`;
        div.textContent = text;

        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;

        return div;
    }

    // ---------- Send ----------
    async function sendMessage() {
        const question = input.value.trim();

        if (!question) {
            return;
        }

        input.value = "";

        addMessage(question, "user");

        const thinking = addMessage("Thinking...", "assistant");

        send.disabled = true;
        input.disabled = true;

        try {
            const response = await fetch(ENDPOINT, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    messages: [
                        {
                            role: "system",
                            content:
                                "You are the c4dynamics documentation assistant. " +
                                "Answer questions using the c4dynamics documentation provided by the retrieval system. " +
                                "Be technically precise. Do not invent APIs or functionality. " +
                                "If the documentation does not contain the answer, say that you cannot find it in the documentation."
                        },
                        {
                            role: "user",
                            content: question
                        }
                    ]
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            const answer =
                data.choices?.[0]?.message?.content ||
                data.result?.response ||
                "Sorry, I couldn't generate an answer.";

            thinking.textContent = answer;

        } catch (error) {
            console.error("c4dynamics chatbot error:", error);
            thinking.textContent =
                "Sorry, the documentation assistant is currently unavailable.";
        }

        send.disabled = false;
        input.disabled = false;
        input.focus();
    }

    send.addEventListener("click", sendMessage);

    input.addEventListener("keydown", event => {
        if (event.key === "Enter") {
            sendMessage();
        }
    });
});