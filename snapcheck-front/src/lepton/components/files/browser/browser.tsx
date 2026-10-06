import type { DirectoryItemModel, DirectoryModel } from '@lepton/api-client';
import type React from 'react';
import { useEffect, useState } from 'react';
import { useFileServices } from '../../../../api/snapServices';

import './browser.css';
import { Folder } from '@mui/icons-material';
import ClearIcon from '@mui/icons-material/Clear';
import SearchIcon from '@mui/icons-material/Search';
import Button from '../../lib/button';

const FilesBrowser: React.FC<{
    path: string | null;
    extensions?: string[];
    onFileSelect?: (file: string) => void;
    onPathChange?: (path: string | null) => void;
}> = ({ path, extensions, onFileSelect, onPathChange }) => {
    const [, setIsLoading] = useState(false);
    const [directory, setDirectory] = useState<DirectoryModel | null>(null);
    const [search, setSearch] = useState('');
    const fileServices = useFileServices();

    useEffect(() => {
        const fetchFiles = async () => {
            setIsLoading(true);
            try {
                const directory = await fileServices.listDirectory(path || undefined, extensions);
                setDirectory(directory);
            } catch (error) {
                console.error('Error fetching directory:', error);
            }
            setIsLoading(false);
        };

        fetchFiles();
    }, [path]);

    const handleFileSelect = (item: DirectoryItemModel) => {
        if (item.isdir) {
            if (onPathChange) {
                onPathChange(item.path);
            }
        } else if (onFileSelect) {
            onFileSelect(item.path);
        }
    };

    const goto = (p: string | null) => {
        if (onPathChange) {
            onPathChange(p);
        }
    };

    const updateSarch = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSearch(event.target.value);
    };

    const handleSearchKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Escape') {
            setSearch('');
            event.stopPropagation();
        }
    };

    const breadcrumbs: JSX.Element[] = [];
    if (path) {
        const parts = path.split('/').filter(Boolean);
        breadcrumbs.push(
            <Button className="separator" onClick={() => goto('/')}>
                /
            </Button>,
        );
        parts.forEach((part, idx) => {
            const cumPath = parts.slice(0, idx + 1).join('/');
            breadcrumbs.push(
                <span key={cumPath}>
                    <Button onClick={() => goto('/' + cumPath)}>{part}</Button>
                    {idx < parts.length - 1 && <span className="separator">/</span>}
                </span>,
            );
        });
    }
    return (
        <div className="files-browser">
            <div className="files-browser-breadcrumbs">{breadcrumbs}</div>
            <div className="files-filter-bar">
                <input
                    type="text"
                    placeholder="Search..."
                    value={search}
                    onChange={(event) => updateSarch(event)}
                    onKeyDown={handleSearchKeyDown}
                />
                <SearchIcon />
                {search && <ClearIcon onClick={() => setSearch('')} />}
            </div>
            {directory && (
                <ul className="files-browser-items">
                    {directory.parent != null && <li onClick={() => goto(directory.parent ?? null)}>..</li>}
                    {directory?.content
                        .filter((item) => item.filename.toLowerCase().includes(search.toLowerCase()))
                        .map((item) => (
                            <li
                                key={item.path}
                                onClick={() => {
                                    if (item.isdir) goto(item.path);
                                }}
                                onDoubleClick={() => {
                                    if (!item.isdir) handleFileSelect(item);
                                }}
                                className={item.isdir ? 'fb-dir-item' : ''}
                            >
                                {item.isdir && <Folder className="fb-item-icon" />}
                                <span>{item.filename}</span>
                            </li>
                        ))}
                </ul>
            )}
        </div>
    );
};

export default FilesBrowser;
