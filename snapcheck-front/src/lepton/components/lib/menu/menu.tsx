import type React from 'react';
import { useState } from 'react';
import './menu.css';

type MenuItemAction = {
    type?: 'item';
    label: string;
    onClick?: () => void;
    disabled?: boolean;
    checked?: boolean;
    children?: MenuItem[];
};
type MenuItemSeparator = {
    type: 'separator';
};
type MenuItem = MenuItemAction | MenuItemSeparator;

const SubMenu: React.FC<{
    items: MenuItem[];
}> = ({ items }) => {
    const [openIndex, setOpenIndex] = useState<number | null>(null);

    return (
        <div className="menu-dropdown">
            {items.map((child, idx) =>
                child.type === 'separator' ? (
                    <div key={`separator-${idx}`} className="menu-separator"></div>
                ) : (
                    <div
                        key={child.label}
                        className={'menu-inner-item' + (child.children && openIndex === idx ? ' open' : '')}
                        onClick={child.onClick}
                        tabIndex={0}
                        aria-disabled={child.disabled}
                        onMouseEnter={() => setOpenIndex(idx)}
                        onMouseLeave={() => setOpenIndex(null)}
                    >
                        <span className="grow">
                            {child.checked !== undefined && (
                                <span className={'menu-checkbox' + (child.checked ? ' checked' : '')} />
                            )}
                            {child.label}
                        </span>
                        {child.children && <span className="submenu-arrow">▶</span>}
                        {child.children && openIndex === idx && (
                            <div className="submenu-child">
                                <SubMenu items={child.children} />
                            </div>
                        )}
                    </div>
                ),
            )}
        </div>
    );
};

type MenuProps = {
    items: MenuItem[];
};

const Menu: React.FC<MenuProps> = ({ items }) => {
    const [openIndex, setOpenIndex] = useState<number | null>(null);

    const childs = items.map((item, idx) =>
        item.type === 'separator' ? (
            <div key={`sep-${idx}`} className="menu-separator" />
        ) : (
            <div
                key={idx}
                className={'menu-item' + (openIndex === idx ? ' open' : '')}
                onClick={() => {
                    if (openIndex === idx) setOpenIndex(null);
                    else setOpenIndex(idx);
                }}
                onMouseOver={() => {
                    if (openIndex !== null) setOpenIndex(idx);
                }}
                onMouseLeave={() => setOpenIndex(null)}
            >
                <div className="menu-button" onClick={item.onClick} tabIndex={idx}>
                    {item.label}
                </div>
                {item.children && openIndex === idx && <SubMenu items={item.children} />}
            </div>
        ),
    );

    return <nav className="menu">{childs}</nav>;
};

export type { MenuItem, MenuProps };
export default Menu;
