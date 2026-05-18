# Phân Tích Luồng Dữ Liệu - Caro Pro (`TicTacToe.cs`)

Tài liệu này phân tích các luồng dữ liệu (data flows) chính trong mã nguồn trò chơi Caro Pro (File `TicTacToe.cs`). Các luồng dữ liệu mô tả cách thông tin di chuyển giữa Giao diện người dùng (UI), Trạng thái hệ thống (State), và Logic xử lý (Logic).

---

## 1. Luồng Khởi Tạo & Đặt Lại Trò Chơi (Initialization & Reset Flow)
**Mô tả:** Luồng này thiết lập trạng thái ban đầu của trò chơi hoặc làm mới lại bảng khi người chơi chọn "Chơi Lại" hoặc thay đổi cài đặt.

**Chi tiết luồng:**
- **Trigger:** Constructor `GameForm()` khi mở ứng dụng, hoặc nút "Chơi Lại" / đổi cài đặt gọi `RestartGame()`.
- **Dữ liệu di chuyển:** Các biến trạng thái được đưa về giá trị gốc. Mảng `board` bị ghi đè thành giá trị 0, Giao diện (Text của `buttons`) bị làm rỗng.

**Code liên quan:**
```csharp
// Constructor GameForm() - Thiết lập UI và gán Tag tọa độ
buttons[i, j].Tag = new Point(i, j); // Lưu tọa độ vào Tag của Button (Dòng 157)
buttons[i, j].Click += new EventHandler(Button_Click);

// Phương thức RestartGame() (Dòng 418 - 434)
xTurn = true;
turnCount = 0;
gameOver = false;
moveHistory.Clear(); // Xóa lịch sử nước đi

// Vòng lặp reset mảng dữ liệu và UI
board[i, j] = 0; // Đặt lại dữ liệu logic mảng 2 chiều
buttons[i, j].Text = ""; // Xóa hiển thị trên UI
```

---

## 2. Luồng Người Chơi Đánh Cờ (Player Move Flow)
**Mô tả:** Diễn ra khi người dùng click vào một ô trên bàn cờ. Dữ liệu từ giao diện được đẩy vào logic để xử lý nước đi.

**Chi tiết luồng:**
- **Trigger:** Sự kiện `Button_Click` (Dòng 229).
- **Dữ liệu di chuyển (UI -> Logic):** Ép kiểu `sender` thành Button, lấy tọa độ `Point` từ thuộc tính `Tag` đã gán khi khởi tạo.
- **Kiểm tra:** Nếu trò chơi kết thúc (`gameOver`) hoặc ô đã có người đánh (`board[r, c] != 0`), luồng bị hủy.
- **Thực thi:** Gọi `PerformMove(r, c)`. Nếu chơi với máy và tới lượt máy, tiếp tục gọi `MakeBotMove()`.

**Code liên quan:**
```csharp
// Phương thức Button_Click (Dòng 229 - 247)
Button btn = (Button)sender;
Point p = (Point)btn.Tag; // Lấy tọa độ từ UI
int r = p.X; int c = p.Y;

if (board[r, c] != 0) return; // Chặn đánh đè

PerformMove(r, c); // Chuyển dữ liệu vào Logic để xử lý

// Kích hoạt Bot sau khi người chơi đánh
if (!gameOver && playWithBotCheckBox.Checked && !xTurn) {
    Application.DoEvents(); // Giúp UI cập nhật trước khi Bot tính toán
    MakeBotMove();
}
```

---

## 3. Luồng Cập Nhật Trạng Thái Bàn Cờ (Game State Update Flow)
**Mô tả:** Hàm cốt lõi chịu trách nhiệm ghi nhận dữ liệu xuống mảng trạng thái, cập nhật giao diện, lưu lịch sử và kiểm tra thắng thua.

**Chi tiết luồng:**
- **Dữ liệu di chuyển (Logic -> State -> UI):** Tọa độ `(r, c)` được dùng để gán giá trị 1 hoặc 2 vào mảng `board`. Giao diện `buttons` được đổi Text ("X" hoặc "O") và màu sắc.
- **Lưu lịch sử:** Tọa độ được đẩy vào `Stack<Point> moveHistory`.
- **Kiểm tra kết quả:** Hàm `CheckWinner` đọc mảng `board` theo 4 hướng.
  - *Nếu thắng hoặc hòa:* Cập nhật điểm (`xWins`, `oWins`, `drawCount`), cập nhật UI thống kê và bật cờ `gameOver`.
  - *Nếu tiếp tục:* Đổi lượt (`xTurn = !xTurn`) và cập nhật nhãn trạng thái UI.

**Code liên quan:**
```csharp
// Phương thức PerformMove (Dòng 249 - 277)
board[r, c] = player; // Cập nhật mảng Logic
buttons[r, c].Text = xTurn ? "X" : "O"; // Cập nhật UI
moveHistory.Push(new Point(r, c)); // Ghi nhận lịch sử cho Undo

if (CheckWinner(r, c, player)) { ... } // Kiểm tra duyệt mảng 4 hướng
```

---

## 4. Luồng Xử Lý Của Máy (Bot AI Move Flow)
**Mô tả:** Máy phân tích mảng dữ liệu `board` hiện tại để tính toán ra vị trí đánh tối ưu nhất.

**Chi tiết luồng:**
- **Trigger:** Được gọi từ `Button_Click` sau nước đi của người chơi.
- **Đọc cấu hình:** Lấy mức độ khó `difficultyComboBox.SelectedIndex`.
- **Phân tích (State -> Logic):** Quét toàn bộ mảng `board`. Tại mỗi ô trống, giả lập đánh thử và dùng `EvaluateSpot`, `EvaluateLine` để cho điểm tấn công và phòng thủ dựa trên cấu trúc các quân cờ lân cận.
- **Ra quyết định (Logic -> State):** Lưu lại điểm số cao nhất. Khi tìm ra vị trí tốt nhất `(bestR, bestC)`, dữ liệu được truyền ngược lại hàm `PerformMove` để áp dụng nước đi.

**Code liên quan:**
```csharp
// Phương thức MakeBotMove (Dòng 279 - 346)
int diffIndex = difficultyComboBox.SelectedIndex; // Đọc thông số UI

// Lặp toàn bộ mảng board để tìm vị trí trống (Dòng 316-340)
int attackScore = EvaluateSpot(i, j, 2);
int defenseScore = ignoreDefense ? 0 : EvaluateSpot(i, j, 1);
// Thuật toán chấm điểm và chọn vị trí bestR, bestC

if (bestR != -1 && bestC != -1) {
    PerformMove(bestR, bestC); // Gửi kết quả ngược lại luồng State Update
}
```

---

## 5. Luồng Hoàn Tác (Undo Data Flow)
**Mô tả:** Đảo ngược các thay đổi trạng thái gần nhất bằng cách lấy dữ liệu từ ngăn xếp lịch sử.

**Chi tiết luồng:**
- **Trigger:** Nút "Đi Lại (Undo)" gọi `UndoMove()`.
- **Đọc dữ liệu (History -> Logic):** Rút (Pop) tọa độ `Point` cuối cùng từ `moveHistory`. Số lần lấy phụ thuộc vào chế độ: Lấy 1 lần (đánh 2 người) hoặc 2 lần (đánh với máy).
- **Phục hồi (Logic -> State -> UI):** Tại tọa độ vừa lấy, xóa giá trị logic (`board[r, c] = 0`), xóa giá trị hiển thị trên UI (`buttons[r,c].Text = ""`), giảm `turnCount` và đảo lượt `xTurn`.

**Code liên quan:**
```csharp
// Phương thức UndoMove (Dòng 192 - 216)
Point lastMove = moveHistory.Pop(); // Rút dữ liệu khỏi Stack
int r = lastMove.X; int c = lastMove.Y;

board[r, c] = 0; // Hoàn tác mảng Logic
buttons[r, c].Text = ""; // Hoàn tác UI
xTurn = !xTurn; // Trả lại lượt
```

---

## 6. Luồng Quản Lý Điểm Số Và Thống Kê (Statistics Flow)
**Mô tả:** Đảm bảo điểm số nội bộ (logic) được đồng bộ hóa nhất quán lên giao diện hiển thị cho người chơi.

**Chi tiết luồng:**
- **Trigger:** Khi ván cờ kết thúc (có người thắng hoặc hòa) từ trong `PerformMove`, hoặc khi người dùng ấn nút "Xóa Điểm".
- **Dữ liệu di chuyển:** Các biến `xWins`, `oWins`, `drawCount` được thay đổi giá trị. Sau đó, hàm `UpdateStatsUI()` đẩy các biến integer này nối vào chuỗi string trên các Label (UI).

**Code liên quan:**
```csharp
// Cập nhật sau khi kiểm tra Winner trong PerformMove
if (player == 1) xWins++; else oWins++;
UpdateStatsUI();

// Hàm đồng bộ UI (Dòng 179 - 184)
private void UpdateStatsUI()
{
    xWinsLabel.Text = "Thắng (X): " + xWins;
    oWinsLabel.Text = "Thắng (O): " + oWins;
    drawsLabel.Text = "Hòa: " + drawCount;
}

// Xóa điểm (Dòng 218 - 227)
xWins = 0; oWins = 0; drawCount = 0; // Reset biến nội bộ
UpdateStatsUI(); // Gọi đồng bộ lên UI
```
