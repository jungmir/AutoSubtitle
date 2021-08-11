import React, { Component } from "react";
import "./FileUploader.css";

export default class FileUploader extends Component {
    constructor(props) {
        super(props);
        this.state = { uploadFileList: [] };
        this.fileUploader = null;
        this.fileDragAndDrop = this.fileDragAndDrop.bind(this);
        this.readFile = this.readFile.bind(this);
    }
    async readFile(item) {
        const $this = this;
        let filerReader = new FileReader();
        filerReader.onload = await function (e) {
            console.log(e.target.result);
            $this.setState({
                uploadFileList: [
                    ...$this.state.uploadFileList,
                    {
                        name: item.name,
                        size: item.size,
                        type: item.type,
                        path: e.target.result,
                        lastModified: item.lastModified,
                        lastModifiedDate: item.lastModifiedDate,
                    },
                ],
            });
        };
        filerReader.readAsDataURL(item);
    }
    fileDragAndDrop(props) {
        if (this.fileUploader.files) {
            const $this = this;
            Array.prototype.forEach.call(this.fileUploader.files, (item) => {
                this.readFile(item);
                console.log($this.state.uploadFileList);
            });
        }
    }

    componentDidMount() {
        const $this = this;
        this.fileUploader.ondragover = () =>
            $this.fileUploader.classList.add("drop-over");
        this.fileUploader.ondragleave = () =>
            $this.fileUploader.classList.remove("drop-over");
    }
    render() {
        return (
            <section className="file-upload-section">
                <article className="file-dnd">
                    <div className="outbound">
                        <label className="wrapper">
                            <h1>Drag and Drop files here</h1>
                            <input
                                id="file-uploader"
                                type="file"
                                accept="video/*"
                                ref={(ref) => {
                                    this.fileUploader = ref;
                                }}
                                onChange={this.fileDragAndDrop}
                                multiple
                            />
                        </label>
                    </div>
                </article>
                <article className="file-list">
                    <ul>
                        {this.state.uploadFileList ? (
                            <li>{this.state.uploadFileList.name}</li>
                        ) : (
                            ""
                        )}
                    </ul>
                </article>
            </section>
        );
    }
}
