/**
 * 產險懶人包：建立「回報缺漏名詞」Google 表單
 *
 * 使用方式（只需做一次）：
 * 1. 用你的 Google 帳號打開 https://script.google.com ，按「新專案」。
 * 2. 刪掉編輯器裡原本的內容，把這整份貼上，按儲存（磁碟圖示）。
 * 3. 上方函式選單選「createReportForm」，按「執行」。
 *    第一次會要求授權：選你的帳號 →「進階」→「前往（不安全）」→「允許」。
 *    （這是你自己寫的腳本，Google 對未審核的腳本都會這樣提示。）
 * 4. 執行完，下方「執行紀錄」會印出三個網址：
 *    - 填寫網址：給網站用，請複製給 Claude
 *    - 編輯網址：你自己修改表單用
 *    - 回覆試算表：查看大家的回報
 */
function createReportForm() {
  var form = FormApp.create('產險懶人包｜回報缺漏名詞');
  form.setDescription(
    '找不到想查的產險名詞，或發現說明有誤？歡迎告訴我們，我們會整理後補進「產險懶人包」。\n' +
    '本表單不需登入、不蒐集個人資料。'
  );
  form.setCollectEmail(false);
  // 不呼叫 setRequireLogin：個人 Gmail 帳號會出現「系統不支援此項作業」；個人帳號建立的表單本來就不需登入
  form.setLimitOneResponsePerUser(false);
  form.setAllowResponseEdits(false);
  form.setShowLinkToRespondAgain(true);
  form.setConfirmationMessage('感謝回報！我們會盡快整理更新。');

  form.addMultipleChoiceItem()
    .setTitle('回報類型')
    .setChoiceValues(['缺漏名詞（想查但網站沒有）', '說明有誤或不清楚', '其他建議'])
    .setRequired(true);

  form.addTextItem()
    .setTitle('名詞')
    .setHelpText('例：自負額、代位求償、59D1')
    .setRequired(true);

  form.addListItem()
    .setTitle('大概屬於哪個分類？')
    .setChoiceValues(['不確定', '商品專區', '通用名詞', '汽車險', '機車險', '旅平險',
                      '健康傷害險', '責任險', '住火險', '商業火險', '工程水險'])
    .setRequired(false);

  form.addParagraphTextItem()
    .setTitle('補充說明')
    .setHelpText('在哪裡看到這個名詞、想知道什麼，或哪裡寫得不對')
    .setRequired(false);

  // 回覆存到新的試算表
  var ss = SpreadsheetApp.create('產險懶人包｜回報缺漏名詞（回覆）');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  Logger.log('填寫網址（給網站用）：' + form.getPublishedUrl());
  Logger.log('編輯網址（你自己用）：' + form.getEditUrl());
  Logger.log('回覆試算表：' + ss.getUrl());
}
