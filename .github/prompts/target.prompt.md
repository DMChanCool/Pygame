---
mode: agent
tools: ['codebase', 'editFiles', 'fetch', 'problems', 'runCommands', 'search', 'searchResults', 'terminalLastCommand', 'terminalSelection', 'usages']
---

# 開發步驟

-   遵守開發規範
- 請修改 #file:class14/prj14.py
請使用 load_doodle_sprites(): 指令載入圖片
請幫我將角色、平台以及彈簧改成image資料夾當中的照片圖案，如果找不到照片使用原本的方塊圖案顯示
將背景換成白色、文字改為黑色
垂直速度小於0表示上升（跳躍中）
反之當垂直速度大於0表示下降

新增變數facing_right
當direction>0，facing_right=True，反之。
預設面相為右邊

新增變數jumping紀錄玩家跳躍狀態
如果有載入照片的話，確認角色存在，根據角色當前狀態選擇適合的圖片，調整大小為實際尺寸，繪製到視窗上面，如果找不到該角色照片就使用原本的方形