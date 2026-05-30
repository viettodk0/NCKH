# Hướng Dẫn Mở Rộng Dự Án Caro Pro (Tic-Tac-Toe)

Tài liệu này cung cấp các gợi ý, phương pháp và hướng dẫn mã nguồn chi tiết để mở rộng dự án Caro hiện tại (`TicTacToe.cs`). Dự án hiện tại đang sử dụng Windows Forms với bàn cờ $15 \times 15$, hỗ trợ chơi 2 người, chơi với Máy (AI đơn giản dựa trên chấm điểm heuristic 1-ply) và tính năng Đi lại (Undo).

Dưới đây là 5 hướng phát triển lớn giúp dự án trở nên chuyên nghiệp, tối ưu và giàu tính năng hơn.

---

## 1. Nâng Cấp Luật Chơi Caro Chuẩn Quốc Tế (Game Rules)

### 1.1. Luật Chặn Hai Đầu (Block at Both Ends)
*   **Vấn đề hiện tại:** Hàm `CheckWinner` chỉ đếm đủ 5 quân cờ liên tiếp là thắng, chưa áp dụng luật chặn hai đầu (nếu chuỗi 5 quân bị chặn bởi đối thủ ở cả hai đầu thì không được tính là chiến thắng).
*   **Hướng mở rộng:** Cập nhật hàm `CheckWinner` để kiểm tra xem hai đầu của chuỗi 5 quân cờ có bị chặn bởi quân đối phương hay không.

```csharp
private bool CheckWinner(int r, int c, int player)
{
    int[] dr = { 1, 0, 1, 1 };
    int[] dc = { 0, 1, 1, -1 };
    int opponent = (player == 1) ? 2 : 1;

    for (int k = 0; k < 4; k++)
    {
        int count = 1;
        
        // Đi về phía trước
        int i1 = r + dr[k], j1 = c + dc[k];
        while (i1 >= 0 && i1 < boardSize && j1 >= 0 && j1 < boardSize && board[i1, j1] == player) 
        { 
            count++; 
            i1 += dr[k]; 
            j1 += dc[k]; 
        }
        
        // Đi về phía sau
        int i2 = r - dr[k], j2 = c - dc[k];
        while (i2 >= 0 && i2 < boardSize && j2 >= 0 && j2 < boardSize && board[i2, j2] == player) 
        { 
            count++; 
            i2 -= dr[k]; 
            j2 -= dc[k]; 
        }

        if (count >= 5)
        {
            // Kiểm tra xem hai đầu có bị chặn không
            bool openHead1 = true;
            bool openHead2 = true;

            // Kiểm tra đầu 1 (phía trước)
            if (i1 < 0 || i1 >= boardSize || j1 < 0 || j1 >= boardSize || board[i1, j1] == opponent)
                openHead1 = false;

            // Kiểm tra đầu 2 (phía sau)
            if (i2 < 0 || i2 >= boardSize || j2 < 0 || j2 >= boardSize || board[i2, j2] == opponent)
                openHead2 = false;

            // Nếu bị chặn cả hai đầu thì không thắng (chỉ áp dụng khi có đúng hoặc lớn hơn 5 quân)
            if (!openHead1 && !openHead2)
                continue; // Chưa thắng ở hướng này, kiểm tra hướng tiếp theo

            return true;
        }
    }
    return false;
}
```

### 1.2. Thêm Bộ Đếm Thời Gian Cho Mỗi Lượt (Turn Timer)
*   Thêm một thanh tiến trình (`ProgressBar`) hoặc một `Label` đếm ngược thời gian (ví dụ: 15 giây/lượt).
*   Sử dụng component `System.Windows.Forms.Timer` để giảm thời gian mỗi giây. Nếu hết thời gian mà người chơi chưa đi, lượt chơi sẽ tự động chuyển sang người kia (hoặc xử thua).

---

## 2. Tối Ưu Hóa Giao Diện & Hiệu Năng (UI/UX Customization)

### 2.1. Vẽ Bàn Cờ Trực Tiếp Bằng GDI+ thay vì sử dụng 225 Ô Buttons
*   **Vấn đề hiện tại:** Bàn cờ đang được xây dựng từ 225 Control `Button`. Càng nhiều Control thì việc tải giao diện càng chậm và có thể gây giật màn hình khi thay đổi kích thước.
*   **Hướng mở rộng:** Kế thừa từ `Panel` hoặc vẽ trực tiếp trên Form bằng sự kiện `OnPaint` và sử dụng kỹ thuật **Double Buffering** để vẽ mượt mà, không bị nhấp nháy.

```csharp
// Trong Constructor của Custom Board Panel:
this.DoubleBuffered = true;

protected override void OnPaint(PaintEventArgs e)
{
    base.OnPaint(e);
    Graphics g = e.Graphics;
    g.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.AntiAlias;

    // Vẽ lưới bàn cờ
    Pen gridPen = new Pen(Color.LightGray, 1);
    for (int i = 0; i <= boardSize; i++)
    {
        // Vẽ các đường dọc và ngang
        g.DrawLine(gridPen, i * buttonSize, 0, i * buttonSize, boardSize * buttonSize);
        g.DrawLine(gridPen, 0, i * buttonSize, boardSize * buttonSize, i * buttonSize);
    }

    // Vẽ quân cờ X và O đẹp hơn từ mảng dữ liệu board[,]
    for (int r = 0; r < boardSize; r++)
    {
        for (int c = 0; c < boardSize; c++)
        {
            Rectangle rect = new Rectangle(c * buttonSize + 3, r * buttonSize + 3, buttonSize - 6, buttonSize - 6);
            if (board[r, c] == 1) // Vẽ quân X bằng bút vẽ dày, màu Crimson
            {
                using (Pen penX = new Pen(Color.Crimson, 3))
                {
                    g.DrawLine(penX, rect.Left, rect.Top, rect.Right, rect.Bottom);
                    g.DrawLine(penX, rect.Right, rect.Top, rect.Left, rect.Bottom);
                }
            }
            else if (board[r, c] == 2) // Vẽ quân O bằng vòng tròn màu SeaGreen
            {
                using (Pen penO = new Pen(Color.MediumSeaGreen, 3))
                {
                    g.DrawEllipse(penO, rect);
                }
            }
        }
    }
}
```
*   **Xử lý nhấp chuột:** Bắt sự kiện `MouseClick` của Panel để tính toán tọa độ dòng/cột dựa trên vị trí chuột click: `int col = e.X / buttonSize; int row = e.Y / buttonSize;`

### 2.2. Hỗ Trợ Chế Độ Sáng/Tối (Light/Dark Mode)
*   Thêm nút chuyển đổi giao diện (Theme Switcher).
*   Định nghĩa bộ màu sắc (Palette) cho Light và Dark mode:
    *   **Light:** Nền trắng, lưới xám nhạt, màu chữ tối.
    *   **Dark:** Nền xám đậm (`Color.FromArgb(30, 30, 35)`), lưới cờ xám tối (`Color.FromArgb(60, 60, 65)`), nút màu neon dịu mắt.

---

## 3. Cải Tiến Trí Tuệ Nhân Tạo (AI / Bot Upgrades)

### 3.1. Thuật Toán Tìm Kiếm Minimax Kết Hợp Cắt Tỉa Alpha-Beta
*   **Hiện tại:** Bot chỉ đánh dựa trên nước đi trực diện có điểm số cao nhất ngay lập tức (1-ply Heuristic).
*   **Hướng mở rộng:** Để Bot có thể nhìn xa trông rộng (2-4 nước cờ tiếp theo), ta cần xây dựng thuật toán tìm kiếm nước đi tối ưu bằng cây quyết định Minimax:

```csharp
private int Minimax(int[,] currentBoard, int depth, int alpha, int beta, bool isMaxPlayer)
{
    // 1. Kiểm tra trạng thái dừng (thắng, thua, hòa, hoặc đạt độ sâu giới hạn)
    if (depth == 0 || IsGameOver(currentBoard))
    {
        return EvaluateBoardForAI(currentBoard);
    }

    // 2. Lấy danh sách các nước đi tiềm năng để giảm số nhánh duyệt (Heuristic Cutoff)
    var candidateMoves = GetCandidateMoves(currentBoard);

    if (isMaxPlayer)
    {
        int maxEval = int.MinValue;
        foreach (var move in candidateMoves)
        {
            currentBoard[move.X, move.Y] = 2; // Giả lập AI đi
            int eval = Minimax(currentBoard, depth - 1, alpha, beta, false);
            currentBoard[move.X, move.Y] = 0; // Hoàn tác
            maxEval = Math.Max(maxEval, eval);
            alpha = Math.Max(alpha, eval);
            if (beta <= alpha) break; // Cắt tỉa Beta
        }
        return maxEval;
    }
    else
    {
        int minEval = int.MaxValue;
        foreach (var move in candidateMoves)
        {
            currentBoard[move.X, move.Y] = 1; // Giả lập Người chơi đi
            int eval = Minimax(currentBoard, depth - 1, alpha, beta, true);
            currentBoard[move.X, move.Y] = 0; // Hoàn tác
            minEval = Math.Min(minEval, eval);
            beta = Math.Min(beta, eval);
            if (beta <= alpha) break; // Cắt tỉa Alpha
        }
        return minEval;
    }
}
```

*   **Tối ưu hóa:** Với bàn cờ $15 \times 15$, việc duyệt hết mọi ô trống là bất khả thi. Vì vậy, hàm `GetCandidateMoves` chỉ nên trả về các ô trống có khoảng cách tối đa 1 hoặc 2 ô tính từ các quân cờ đã được đánh sẵn trên bàn cờ.

---

## 4. Bổ Sung Các Tính Năng Chơi Game Nâng Cao (Game Features)

### 4.1. Chơi Qua Mạng LAN/Internet (Multiplayer)
*   Sử dụng thư viện `System.Net.Sockets` của C# để xây dựng kiến trúc **TCP Client - Server** đơn giản.
*   Một người chơi sẽ mở phòng (đóng vai trò là Server lắng nghe kết nối), người kia nhập địa chỉ IP để tham gia (Client).
*   Giao thức truyền nhận thông điệp dạng chuỗi văn bản (ví dụ gửi: `MOVE;row;col` hoặc `RESTART`).

### 4.2. Xem Lại Trận Đấu (Replay Match) & Lưu/Tải Trận (Save/Load)
*   **Lưu/Tải:** Vì lịch sử trận đấu đã được lưu đầy đủ trong `moveHistory`, bạn có thể chuyển đổi Stack này thành một danh sách JSON hoặc tệp tin Text đơn giản (chứa chuỗi các tọa độ như `7,7; 8,8; 7,8...`) rồi lưu xuống máy.
*   **Xem lại (Replay):** Khi xem lại, khởi động bàn cờ trống, dùng một bộ Timer để tự động thực hiện lại từng nước đi trong lịch sử cách nhau 1-2 giây, cho phép người dùng bấm "Tạm dừng" hoặc "Xem tiếp".

---

## 5. Tách Biệt Kiến Trúc Dự Án (Architecture Refactoring)

### Áp dụng Mô hình MVP (Model-View-Presenter)
*   **Vấn đề hiện tại:** Toàn bộ dữ liệu bàn cờ (`board[,]`), lượt đi, điểm số (Model), logic Bot AI (Logic) và giao diện vẽ Controls, Form (View) đều bị gộp chung vào một lớp `GameForm`. Điều này làm mã nguồn khó mở rộng hoặc chuyển đổi sang Web, Mobile hay Unity.
*   **Cấu trúc đề xuất:**
    1.  **Model:** Lớp `GameModel` quản lý mảng dữ liệu `board[,]`, kiểm tra chiến thắng, đếm số lượt, quản lý điểm số. Lớp này hoàn toàn độc lập, không tham chiếu đến giao diện WinForms.
    2.  **View:** Lớp `IGameView` định nghĩa các hành vi hiển thị giao diện: `UpdateCell(int r, int c, int player)`, `ShowWinner(string msg)`, `ShowStats(int xWins, int oWins, int draws)`.
    3.  **Presenter:** Lớp `GamePresenter` trung gian điều phối luồng xử lý: Nhận tín hiệu người dùng từ View -> Gửi xử lý xuống Model -> Lấy kết quả từ Model -> Yêu cầu View cập nhật giao diện và gọi Bot AI đi tiếp nếu cần.

Việc tách biệt này giúp mã nguồn sạch sẽ, dễ viết kiểm thử tự động (Unit Test) cho logic game và thuật toán AI.
