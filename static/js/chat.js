document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("message-input");
    const sendButton = document.querySelector(".chat-input-send-button");
    const chatApp = document.querySelector(".chat-app");

    // 메시지 추가하는 함수
    function addMessage(content, isUser = true) {
        const messageContainer = document.createElement("div");
        messageContainer.classList.add("chat-message");

        const messageBubble = document.createElement("div");
        messageBubble.classList.add("message-bubble");
        messageBubble.classList.add(isUser ? "user-message" : "assistant-message");

        messageBubble.innerText = content;
        messageContainer.appendChild(messageBubble);
        chatApp.appendChild(messageContainer);

        // 새 메시지를 보여주도록 스크롤을 아래로
        chatApp.scrollTop = chatApp.scrollHeight;
    }

    // 서버로 질문을 전송하는 함수
    async function sendMessage(message) {
        try {
            const response = await fetch("/query/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ question: message })
            });

            const data = await response.json();

            if (response.ok) {
                addMessage(data.answer, false); // AI 응답
            } else {
                addMessage("Error: " + data.detail, false); // 에러 메시지
            }
        } catch (error) {
            addMessage("Error: 서버에 연결할 수 없습니다.", false); // 연결 실패 시
        }
    }

    // 입력 필드에서 Enter 키를 누르면 메시지 전송
    inputField.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
            const message = inputField.value.trim();
            if (message) {
                addMessage(message); // 사용자가 보낸 메시지 추가
                sendMessage(message); // 서버에 메시지 전송
                inputField.value = ""; // 입력 필드 초기화
            }
        }
    });

    // 입력 버튼을 클릭하면 메시지 전송
    sendButton.addEventListener("click", function () {
        const message = inputField.value.trim();
        if (message) {
            addMessage(message); // 사용자가 보낸 메시지 추가
            sendMessage(message); // 서버에 메시지 전송
            inputField.value = ""; // 입력 필드 초기화
        }
    });
});