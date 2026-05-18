using System;
using System.Drawing;
using System.Windows.Forms;

namespace TicTacToe
{
    public class GameForm : Form
    {
        private const int boardSize = 15;
        private const int buttonSize = 30;
        private Button[,] buttons = new Button[boardSize, boardSize];
        private int[,] board = new int[boardSize, boardSize]; // 0: empty, 1: X, 2: O
        private bool xTurn = true;
        private int turnCount = 0;
        private bool gameOver = false;

        private int xWins = 0;
        private int oWins = 0;
        private int drawCount = 0;

        private System.Collections.Generic.Stack<Point> moveHistory = new System.Collections.Generic.Stack<Point>();

        private Label statusLabel;
        private Label xWinsLabel;
        private Label oWinsLabel;
        private Label drawsLabel;
        private Button restartButton;
        private Button undoButton;
        private Button resetScoreButton;
        private CheckBox playWithBotCheckBox;
        private ComboBox difficultyComboBox;

        public GameForm()
        {
            this.Text = "Caro Pro";
            this.ClientSize = new Size(710, 500);
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.StartPosition = FormStartPosition.CenterScreen;
            this.BackColor = Color.FromArgb(245, 245, 250);

            Panel controlPanel = new Panel();
            controlPanel.Size = new Size(220, 480);
            controlPanel.Location = new Point(470, 10);
            controlPanel.BackColor = Color.White;
            controlPanel.BorderStyle = BorderStyle.FixedSingle;
            this.Controls.Add(controlPanel);

            Label titleLabel = new Label();
            titleLabel.Text = "CARO PRO";
            titleLabel.Font = new Font("Segoe UI", 24, FontStyle.Bold);
            titleLabel.ForeColor = Color.DarkSlateBlue;
            titleLabel.Location = new Point(10, 10);
            titleLabel.AutoSize = true;
            controlPanel.Controls.Add(titleLabel);

            statusLabel = new Label();
            statusLabel.Text = "Lượt của: X";
            statusLabel.Font = new Font("Segoe UI", 16, FontStyle.Bold);
            statusLabel.ForeColor = Color.Crimson;
            statusLabel.Location = new Point(10, 60);
            statusLabel.AutoSize = true;
            controlPanel.Controls.Add(statusLabel);

            playWithBotCheckBox = new CheckBox();
            playWithBotCheckBox.Text = "Chơi với Máy";
            playWithBotCheckBox.Location = new Point(15, 110);
            playWithBotCheckBox.AutoSize = true;
            playWithBotCheckBox.Font = new Font("Segoe UI", 12, FontStyle.Regular);
            playWithBotCheckBox.Checked = true;
            playWithBotCheckBox.CheckedChanged += new EventHandler(RestartGame);
            controlPanel.Controls.Add(playWithBotCheckBox);

            Label diffLabel = new Label();
            diffLabel.Text = "Độ khó:";
            diffLabel.Font = new Font("Segoe UI", 10, FontStyle.Regular);
            diffLabel.Location = new Point(15, 145);
            diffLabel.AutoSize = true;
            controlPanel.Controls.Add(diffLabel);

            difficultyComboBox = new ComboBox();
            difficultyComboBox.Items.AddRange(new string[] { "Dễ", "Trung bình", "Khó" });
            difficultyComboBox.SelectedIndex = 1;
            difficultyComboBox.DropDownStyle = ComboBoxStyle.DropDownList;
            difficultyComboBox.Font = new Font("Segoe UI", 10);
            difficultyComboBox.Location = new Point(80, 142);
            difficultyComboBox.Size = new Size(120, 25);
            difficultyComboBox.SelectedIndexChanged += new EventHandler(RestartGame);
            controlPanel.Controls.Add(difficultyComboBox);

            Label sep1 = new Label();
            sep1.BorderStyle = BorderStyle.Fixed3D;
            sep1.Location = new Point(10, 190);
            sep1.Size = new Size(200, 2);
            controlPanel.Controls.Add(sep1);

            Label statsTitle = new Label();
            statsTitle.Text = "THỐNG KÊ";
            statsTitle.Font = new Font("Segoe UI", 12, FontStyle.Bold);
            statsTitle.Location = new Point(10, 210);
            statsTitle.AutoSize = true;
            controlPanel.Controls.Add(statsTitle);

            xWinsLabel = new Label();
            xWinsLabel.Text = "Thắng (X): 0";
            xWinsLabel.Font = new Font("Segoe UI", 12, FontStyle.Regular);
            xWinsLabel.ForeColor = Color.Crimson;
            xWinsLabel.Location = new Point(15, 240);
            xWinsLabel.AutoSize = true;
            controlPanel.Controls.Add(xWinsLabel);

            oWinsLabel = new Label();
            oWinsLabel.Text = "Thắng (O): 0";
            oWinsLabel.Font = new Font("Segoe UI", 12, FontStyle.Regular);
            oWinsLabel.ForeColor = Color.MediumSeaGreen;
            oWinsLabel.Location = new Point(15, 270);
            oWinsLabel.AutoSize = true;
            controlPanel.Controls.Add(oWinsLabel);

            drawsLabel = new Label();
            drawsLabel.Text = "Hòa: 0";
            drawsLabel.Font = new Font("Segoe UI", 12, FontStyle.Regular);
            drawsLabel.Location = new Point(15, 300);
            drawsLabel.AutoSize = true;
            controlPanel.Controls.Add(drawsLabel);

            restartButton = CreateButton("Chơi Lại", new Point(15, 350), Color.DodgerBlue, Color.White);
            restartButton.Click += new EventHandler(RestartGame);
            controlPanel.Controls.Add(restartButton);

            undoButton = CreateButton("Đi Lại (Undo)", new Point(15, 390), Color.DarkOrange, Color.White);
            undoButton.Click += new EventHandler(UndoMove);
            controlPanel.Controls.Add(undoButton);

            resetScoreButton = CreateButton("Xóa Điểm", new Point(15, 430), Color.DimGray, Color.White);
            resetScoreButton.Click += new EventHandler(ResetScore);
            controlPanel.Controls.Add(resetScoreButton);

            Panel boardPanel = new Panel();
            boardPanel.Size = new Size(450, 450);
            boardPanel.Location = new Point(10, 20);
            this.Controls.Add(boardPanel);

            for (int i = 0; i < boardSize; i++)
            {
                for (int j = 0; j < boardSize; j++)
                {
                    buttons[i, j] = new Button();
                    buttons[i, j].Size = new Size(buttonSize, buttonSize);
                    buttons[i, j].Location = new Point(j * buttonSize, i * buttonSize);
                    buttons[i, j].Font = new Font("Arial", 14, FontStyle.Bold);
                    buttons[i, j].FlatStyle = FlatStyle.Flat;
                    buttons[i, j].FlatAppearance.BorderColor = Color.LightGray;
                    buttons[i, j].BackColor = Color.White;
                    buttons[i, j].TabStop = false;
                    buttons[i, j].Cursor = Cursors.Hand;
                    buttons[i, j].Tag = new Point(i, j);
                    buttons[i, j].Click += new EventHandler(Button_Click);
                    boardPanel.Controls.Add(buttons[i, j]);
                }
            }
        }

        private Button CreateButton(string text, Point loc, Color backColor, Color foreColor)
        {
            Button btn = new Button();
            btn.Text = text;
            btn.Location = loc;
            btn.Size = new Size(185, 30);
            btn.Font = new Font("Segoe UI", 10, FontStyle.Bold);
            btn.BackColor = backColor;
            btn.ForeColor = foreColor;
            btn.FlatStyle = FlatStyle.Flat;
            btn.FlatAppearance.BorderSize = 0;
            btn.Cursor = Cursors.Hand;
            return btn;
        }

        private void UpdateStatsUI()
        {
            xWinsLabel.Text = "Thắng (X): " + xWins;
            oWinsLabel.Text = "Thắng (O): " + oWins;
            drawsLabel.Text = "Hòa: " + drawCount;
        }

        private void UpdateStatusLabel()
        {
            statusLabel.Text = "Lượt của: " + (xTurn ? "X" : "O");
            statusLabel.ForeColor = xTurn ? Color.Crimson : Color.MediumSeaGreen;
        }

        private void UndoMove(object sender, EventArgs e)
        {
            if (gameOver || moveHistory.Count == 0) return;

            int undoCount = 1;
            if (playWithBotCheckBox.Checked && moveHistory.Count >= 2 && xTurn) 
            {
                undoCount = 2;
            }

            for (int k = 0; k < undoCount; k++)
            {
                if (moveHistory.Count > 0)
                {
                    Point lastMove = moveHistory.Pop();
                    int r = lastMove.X;
                    int c = lastMove.Y;
                    board[r, c] = 0;
                    buttons[r, c].Text = "";
                    xTurn = !xTurn;
                    turnCount--;
                }
            }
            UpdateStatusLabel();
        }

        private void ResetScore(object sender, EventArgs e)
        {
            if (MessageBox.Show("Bạn có chắc muốn xóa điểm số về 0?", "Xác nhận", MessageBoxButtons.YesNo) == DialogResult.Yes)
            {
                xWins = 0;
                oWins = 0;
                drawCount = 0;
                UpdateStatsUI();
            }
        }

        private void Button_Click(object sender, EventArgs e)
        {
            if (gameOver) return;

            Button btn = (Button)sender;
            Point p = (Point)btn.Tag;
            int r = p.X;
            int c = p.Y;

            if (board[r, c] != 0) return;

            PerformMove(r, c);

            if (!gameOver && playWithBotCheckBox.Checked && !xTurn)
            {
                Application.DoEvents();
                MakeBotMove();
            }
        }

        private void PerformMove(int r, int c)
        {
            int player = xTurn ? 1 : 2;
            board[r, c] = player;
            buttons[r, c].Text = xTurn ? "X" : "O";
            buttons[r, c].ForeColor = xTurn ? Color.Crimson : Color.MediumSeaGreen;
            turnCount++;
            moveHistory.Push(new Point(r, c));

            if (CheckWinner(r, c, player))
            {
                gameOver = true;
                if (player == 1) xWins++; else oWins++;
                UpdateStatsUI();
                MessageBox.Show("Người chơi " + (xTurn ? "X" : "O") + " đã chiến thắng!", "Kết quả");
            }
            else if (turnCount == boardSize * boardSize)
            {
                gameOver = true;
                drawCount++;
                UpdateStatsUI();
                MessageBox.Show("Hòa!", "Kết quả");
            }
            else
            {
                xTurn = !xTurn;
                UpdateStatusLabel();
            }
        }

        private void MakeBotMove()
        {
            if (turnCount == 0)
            {
                PerformMove(boardSize / 2, boardSize / 2);
                return;
            }

            Random rnd = new Random();
            int diffIndex = difficultyComboBox.SelectedIndex; // 0: Dễ, 1: TB, 2: Khó
            
            // Dễ: 70% random quanh khu vực có quân
            if (diffIndex == 0 && rnd.Next(100) < 70)
            {
                System.Collections.Generic.List<Point> available = new System.Collections.Generic.List<Point>();
                for (int i = 0; i < boardSize; i++)
                {
                    for (int j = 0; j < boardSize; j++)
                    {
                        if (board[i, j] == 0 && HasNeighbor(i, j))
                            available.Add(new Point(i, j));
                    }
                }
                if (available.Count > 0)
                {
                    Point p = available[rnd.Next(available.Count)];
                    PerformMove(p.X, p.Y);
                    return;
                }
            }

            int bestScore = -1;
            int bestR = -1;
            int bestC = -1;

            bool ignoreDefense = (diffIndex == 1 && rnd.Next(100) < 30); // TB: 30% quên phòng thủ

            for (int i = 0; i < boardSize; i++)
            {
                for (int j = 0; j < boardSize; j++)
                {
                    if (board[i, j] == 0)
                    {
                        int attackScore = EvaluateSpot(i, j, 2);
                        int defenseScore = ignoreDefense ? 0 : EvaluateSpot(i, j, 1);
                        
                        int score = 0;
                        if (attackScore >= 100000) score = 200000; 
                        else if (defenseScore >= 100000) score = 150000; 
                        else score = (int)(attackScore * 1.1 + defenseScore);

                        score += rnd.Next(10);

                        if (score > bestScore)
                        {
                            bestScore = score;
                            bestR = i;
                            bestC = j;
                        }
                    }
                }
            }

            if (bestR != -1 && bestC != -1)
            {
                PerformMove(bestR, bestC);
            }
        }

        private bool HasNeighbor(int r, int c)
        {
            for (int i = -1; i <= 1; i++)
            {
                for (int j = -1; j <= 1; j++)
                {
                    if (i == 0 && j == 0) continue;
                    int nr = r + i, nc = c + j;
                    if (nr >= 0 && nr < boardSize && nc >= 0 && nc < boardSize && board[nr, nc] != 0)
                        return true;
                }
            }
            return false;
        }

        private int EvaluateSpot(int r, int c, int player)
        {
            int score = 0;
            score += EvaluateLine(r, c, 1, 0, player); 
            score += EvaluateLine(r, c, 0, 1, player); 
            score += EvaluateLine(r, c, 1, 1, player); 
            score += EvaluateLine(r, c, 1, -1, player); 
            return score;
        }

        private int EvaluateLine(int r, int c, int dr, int dc, int player)
        {
            int count = 1;
            int block = 0;

            int i = r + dr, j = c + dc;
            while (i >= 0 && i < boardSize && j >= 0 && j < boardSize && board[i, j] == player) { count++; i += dr; j += dc; }
            if (i < 0 || i >= boardSize || j < 0 || j >= boardSize || board[i, j] != 0) block++;

            i = r - dr; j = c - dc;
            while (i >= 0 && i < boardSize && j >= 0 && j < boardSize && board[i, j] == player) { count++; i -= dr; j -= dc; }
            if (i < 0 || i >= boardSize || j < 0 || j >= boardSize || board[i, j] != 0) block++;

            if (count >= 5) return 100000;
            if (block == 2) return 0;
            if (count == 4 && block == 0) return 10000;
            if (count == 4 && block == 1) return 1000;
            if (count == 3 && block == 0) return 2000;
            if (count == 3 && block == 1) return 100;
            if (count == 2 && block == 0) return 200;
            if (count == 2 && block == 1) return 10;
            if (count == 1 && block == 0) return 10;
            return 0;
        }

        private bool CheckWinner(int r, int c, int player)
        {
            int[] dr = { 1, 0, 1, 1 };
            int[] dc = { 0, 1, 1, -1 };

            for (int k = 0; k < 4; k++)
            {
                int count = 1;
                
                int i = r + dr[k], j = c + dc[k];
                while (i >= 0 && i < boardSize && j >= 0 && j < boardSize && board[i, j] == player) { count++; i += dr[k]; j += dc[k]; }
                
                i = r - dr[k]; j = c - dc[k];
                while (i >= 0 && i < boardSize && j >= 0 && j < boardSize && board[i, j] == player) { count++; i -= dr[k]; j -= dc[k]; }

                if (count >= 5) return true;
            }
            return false;
        }

        private void RestartGame(object sender, EventArgs e)
        {
            xTurn = true;
            turnCount = 0;
            gameOver = false;
            moveHistory.Clear();
            UpdateStatusLabel();

            for (int i = 0; i < boardSize; i++)
            {
                for (int j = 0; j < boardSize; j++)
                {
                    board[i, j] = 0;
                    buttons[i, j].Text = "";
                }
            }
        }

        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new GameForm());
        }
    }
}
