console.log("Spec.js loading");

describe("Superlists tests", () => {
  const inputId = "id_text";
  const errorClass = "invalid-feedback";
  const inputSelector = `#${inputId}`;
  const errorSelector = `.${errorClass}`;
  let testDiv;

  beforeEach(() => {
    console.log("beforeEach");
    testDiv = document.createElement("div");
    testDiv.innerHTML = `
      <form>
        <input
          id="${inputId}"
          name="text"
          class="form-control form-control-lg is-invalid"
          placeholder="Enter a to-do item"
          value="Value as submitted"
          aria-describedby="id_text_feedback"
          required
        />
        <div id="id_text_feedback" class="${errorClass}">An error message</div>
      </form>
    `;
    document.body.appendChild(testDiv);
  });

  afterEach(() => {
    testDiv.remove();
  });

  it("sense-check our html fixture", () => {
    console.log("in test 1");
    const errorMsg = document.querySelector(errorSelector);
    expect(errorMsg.checkVisibility()).toBe(true);
  });

  it("error message should be hidden on input", () => {
    console.log("in test 2");
    const textInput = document.querySelector(inputSelector);
    const errorMsg = document.querySelector(errorSelector);

    initialize();
    textInput.dispatchEvent(new InputEvent("input"));

    expect(errorMsg.checkVisibility()).toBe(false);
  });

  it("error message should not be hidden before input is fired", () => {
    const errorMsg = document.querySelector(errorSelector);
    initialize();
    expect(errorMsg.checkVisibility()).toBe(true);
  });

});
