window.registerInitializer((widget) => {
    new window.Undo({ editor: widget.editor });
});