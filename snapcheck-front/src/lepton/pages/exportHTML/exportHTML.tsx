import { useState } from "react";
import FilesBrowser from "../../components/files/browser/browser";
import { useModal } from "@lepton/core/contexts/ModalContext";

const ExportHTMLPage: React.FC<{ onSubmit: (path: string) => Promise<string | boolean> | string | boolean }> = ({ onSubmit }) => {
    const [currentPath, setCurrentPath] = useState<string>("");
    const [errorMsg, setErrorMsg] = useState<string | null>(null);
    const { hideModal } = useModal();

    const submit = async () => {
        const res = await onSubmit(currentPath);
        if (!res) hideModal();
        else {
            setErrorMsg(typeof res === "string" ? res : "An error occurred while exporting.");
        }
    }

    return <div>
        <h1>Export</h1>
        <h2>HTML</h2>

        <FilesBrowser
            path={currentPath}
            onPathChange={(p) => setCurrentPath(p || "")}
            extensions={[".snpk"]}
        />
        {errorMsg && <p className="error-message">{errorMsg}</p>}
        <button onClick={submit}>Export</button>
    </div>
}

export default ExportHTMLPage;
